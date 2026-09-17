"""
scratch/run_eda.py — Execute the EDA logic directly (no Jupyter needed)
so we can capture all actual numbers for docs/data_profile.md.

STRUCTURAL PROXY NOTICE: The dataset analysed here is a generic IoT
temperature sensor log, NOT real refrigerated-transport telemetry.
"""
from __future__ import annotations

import pathlib
import warnings
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

warnings.filterwarnings('ignore')
sns.set_theme(style='whitegrid', palette='muted', font_scale=1.1)
plt.rcParams['figure.dpi'] = 120

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW_DIR   = REPO_ROOT / "data" / "raw"
DOCS_DIR  = REPO_ROOT / "docs"
DOCS_DIR.mkdir(exist_ok=True)

csv_files = sorted(RAW_DIR.glob("*.csv"))
if not csv_files:
    sys.exit("No CSV in data/raw/ — run data_acquisition.py first.")

CSV_PATH = csv_files[0]
print(f"File: {CSV_PATH.name}  ({CSV_PATH.stat().st_size/1_048_576:.2f} MB)")

df_raw = pd.read_csv(CSV_PATH)

# ── 1. Row count ──────────────────────────────────────────────────────────────
BRIEF_ESTIMATE = 97_600
actual_rows = len(df_raw)
delta = actual_rows - BRIEF_ESTIMATE
sign = '+' if delta >= 0 else ''
print(f"\n=== ROW COUNT ===")
print(f"Actual rows       : {actual_rows:,}")
print(f"Brief estimate    : ~{BRIEF_ESTIMATE:,}")
print(f"Delta             : {sign}{delta:,} ({sign}{100*delta/BRIEF_ESTIMATE:.2f}%)")

# ── 2. Columns & dtypes ───────────────────────────────────────────────────────
print(f"\n=== COLUMNS & DTYPES ===")
for col in df_raw.columns:
    print(f"  {col!r:30s}  dtype={str(df_raw[col].dtype):12s}  nunique={df_raw[col].nunique():6,}  null={df_raw[col].isna().sum():,}")
print(f"\nExact column list: {list(df_raw.columns)}")

# ── 3. Low-cardinality columns ────────────────────────────────────────────────
print("\n=== LOW-CARDINALITY COLUMNS ===")
for col in df_raw.columns:
    if df_raw[col].nunique() <= 20:
        vc = df_raw[col].value_counts(dropna=False).to_dict()
        print(f"  {col!r}: {vc}")

# ── 4. Identify key columns ───────────────────────────────────────────────────
# In/out tag
in_out_col = None
for col in df_raw.columns:
    vals_lower = df_raw[col].dropna().astype(str).str.lower().unique()
    if set(vals_lower).intersection({'in', 'out', 'inside', 'outside'}):
        in_out_col = col; break

# Timestamp column
ts_col = None
for col in df_raw.columns:
    if any(k in col.lower() for k in ('time','date','noted')):
        ts_col = col; break

# Temperature column
temp_col = None
for col in df_raw.select_dtypes(include=[np.number]).columns:
    if 'temp' in col.lower():
        temp_col = col; break
if temp_col is None:
    num_cols = df_raw.select_dtypes(include=[np.number]).columns.tolist()
    if num_cols: temp_col = num_cols[0]

# Sensor/room ID column
id_col = None
exclude = [c for c in [ts_col, in_out_col] if c]
candidates = [c for c in df_raw.columns
              if c not in exclude and df_raw[c].dtype == object]
if candidates:
    cand = min(candidates, key=lambda c: df_raw[c].nunique())
    if df_raw[cand].nunique() <= 200:
        id_col = cand

print(f"\nKey columns identified:")
print(f"  ts_col    : {ts_col!r}")
print(f"  in_out_col: {in_out_col!r}")
print(f"  temp_col  : {temp_col!r}")
print(f"  id_col    : {id_col!r}")

# ── 5. In/out distribution ───────────────────────────────────────────────────
if in_out_col:
    print(f"\n=== IN/OUT TAG: {in_out_col!r} ===")
    vc = df_raw[in_out_col].value_counts(dropna=False)
    pct = df_raw[in_out_col].value_counts(normalize=True, dropna=False)*100
    for v in vc.index:
        print(f"  {str(v):15s} : {vc[v]:,}  ({pct[v]:.2f}%)")

    fig, ax = plt.subplots(figsize=(5,3))
    vc.plot(kind='bar', ax=ax, color=sns.color_palette('muted', len(vc)))
    ax.set_title(f"Distribution of '{in_out_col}' (In/Out tag)")
    ax.set_ylabel("Row count")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f'{int(x):,}'))
    for p in ax.patches:
        ax.annotate(f'{p.get_height():,.0f}',
                    (p.get_x()+p.get_width()/2, p.get_height()),
                    ha='center', va='bottom', fontsize=9)
    plt.tight_layout()
    plt.savefig(DOCS_DIR/'fig_inout_distribution.png', dpi=120)
    plt.close()
    print("  Saved: docs/fig_inout_distribution.png")

# ── 6. Timestamp parsing & date range ────────────────────────────────────────
df = df_raw.copy()
df['ts_parsed'] = pd.to_datetime(df[ts_col], infer_datetime_format=True, errors='coerce')
n_unparsed = df['ts_parsed'].isna().sum() - df_raw[ts_col].isna().sum()
print(f"\n=== TIMESTAMP PARSING: {ts_col!r} ===")
print(f"  Sample raw values : {df_raw[ts_col].head(3).tolist()}")
print(f"  Parse failures    : {n_unparsed:,}")
print(f"  Earliest          : {df['ts_parsed'].min()}")
print(f"  Latest            : {df['ts_parsed'].max()}")
span = df['ts_parsed'].max() - df['ts_parsed'].min()
print(f"  Span              : {span}")

# ── 7. Sampling-interval analysis ────────────────────────────────────────────
df_sorted = df.dropna(subset=['ts_parsed']).sort_values('ts_parsed').reset_index(drop=True)
gaps_all  = df_sorted['ts_parsed'].diff().dt.total_seconds().dropna()

print(f"\n=== SAMPLING INTERVALS (OVERALL) ===")
print(f"  n_gaps    : {len(gaps_all):,}")
print(f"  min   (s) : {gaps_all.min():.1f}")
print(f"  median(s) : {gaps_all.median():.1f}   ({gaps_all.median()/60:.2f} min)")
print(f"  mean  (s) : {gaps_all.mean():.1f}   ({gaps_all.mean()/60:.2f} min)")
print(f"  std   (s) : {gaps_all.std():.1f}")
print(f"  max   (s) : {gaps_all.max():.1f}   ({gaps_all.max()/3600:.2f} h)")
cv = gaps_all.std() / gaps_all.mean() if gaps_all.mean() != 0 else float('nan')
print(f"  CoV       : {cv:.4f}")
if cv > 0.5:
    verdict = f"CoV={cv:.3f} > 0.5 → sampling IS quantitatively irregular."
elif cv > 0.1:
    verdict = f"CoV={cv:.3f} in 0.1–0.5 → mild irregularity."
else:
    verdict = f"CoV={cv:.3f} < 0.1 → sampling is largely REGULAR; 'irregular' claim does NOT hold strongly."
print(f"  Verdict   : {verdict}")

# Per-ID gaps
if id_col:
    print(f"\n=== PER-ID SAMPLING INTERVALS: {id_col!r} ===")
    rows = []
    for gname, gdf in df_sorted.groupby(id_col):
        if len(gdf) < 2: continue
        g_gaps = gdf['ts_parsed'].diff().dt.total_seconds().dropna()
        rows.append({
            'id': gname, 'n_readings': len(gdf),
            'min_s': g_gaps.min(), 'median_s': g_gaps.median(),
            'mean_s': g_gaps.mean(), 'std_s': g_gaps.std(),
            'max_s': g_gaps.max(),
            'CoV': g_gaps.std()/g_gaps.mean() if g_gaps.mean() != 0 else float('nan'),
        })
    per_id = pd.DataFrame(rows).set_index('id').sort_values('n_readings', ascending=False)
    print(per_id.round(2).to_string())

# Histogram
fig, axes = plt.subplots(1, 2, figsize=(12,4))
axes[0].hist(gaps_all/60, bins=80, color='steelblue', edgecolor='none', alpha=0.85)
axes[0].set_title('Inter-reading gaps — full range')
axes[0].set_xlabel('Gap (minutes)'); axes[0].set_ylabel('Count')
p95 = float(gaps_all.quantile(0.95))
zoomed = gaps_all[gaps_all <= p95]
axes[1].hist(zoomed/60, bins=80, color='darkorange', edgecolor='none', alpha=0.85)
axes[1].set_title(f'Gaps zoomed to p95 ({p95/60:.1f} min)')
axes[1].set_xlabel('Gap (minutes)'); axes[1].set_ylabel('Count')
plt.tight_layout()
plt.savefig(DOCS_DIR/'fig_sampling_intervals.png', dpi=120)
plt.close()
print("\n  Saved: docs/fig_sampling_intervals.png")

# ── 8. Missing values ────────────────────────────────────────────────────────
print("\n=== MISSING VALUES ===")
total_mv = df_raw.isna().sum().sum()
for col in df_raw.columns:
    n = df_raw[col].isna().sum()
    pct = 100*n/len(df_raw)
    print(f"  {col!r:30s}: {n:,} ({pct:.4f}%)")
print(f"  Total missing cells: {total_mv:,} ({100*total_mv/df_raw.size:.6f}% of all cells)")

# ── 9. Duplicate rows ────────────────────────────────────────────────────────
n_dups = df_raw.duplicated().sum()
print(f"\n=== DUPLICATE ROWS ===")
print(f"  Exact duplicates: {n_dups:,}  ({100*n_dups/len(df_raw):.4f}%)")

# ── 10. Temperature stats ────────────────────────────────────────────────────
t = df_raw[temp_col].dropna()
print(f"\n=== TEMPERATURE STATS: {temp_col!r} ===")
print(f"  count : {len(t):,}")
print(f"  min   : {t.min():.4f}")
print(f"  mean  : {t.mean():.4f}")
print(f"  median: {t.median():.4f}")
print(f"  std   : {t.std():.4f}")
print(f"  max   : {t.max():.4f}")
print(f"  Values < -50  : {(t < -50).sum():,}")
print(f"  Values > 100  : {(t > 100).sum():,}")
print(f"  Values == -99 : {(t == -99).sum():,}")
print(f"  Values == 999 : {(t == 999).sum():,}")
print(f"  Values == 0   : {(t == 0).sum():,}")

fig, axes = plt.subplots(1, 2, figsize=(12,4))
t.plot(kind='hist', bins=80, ax=axes[0], color='steelblue', edgecolor='none', alpha=0.85)
axes[0].set_title(f"Temperature distribution ('{temp_col}')"); axes[0].set_xlabel('Temperature'); axes[0].set_ylabel('Count')
t.plot(kind='box', ax=axes[1], color='steelblue')
axes[1].set_title(f"Temperature boxplot ('{temp_col}')"); axes[1].set_ylabel('Temperature')
plt.tight_layout()
plt.savefig(DOCS_DIR/'fig_temperature_distribution.png', dpi=120)
plt.close()
print("  Saved: docs/fig_temperature_distribution.png")

# ── 11. Sensor ID cardinality ────────────────────────────────────────────────
if id_col:
    print(f"\n=== SENSOR/ROOM ID: {id_col!r} ===")
    vc = df_raw[id_col].value_counts()
    print(f"  Unique IDs      : {df_raw[id_col].nunique():,}")
    print(f"  Min readings/id : {vc.min():,}")
    print(f"  Max readings/id : {vc.max():,}")
    print(f"  Mean readings/id: {vc.mean():.1f}")
    print(f"  Top values:\n{vc.head(20).to_string()}")
    if df_raw[id_col].nunique() <= 50:
        fig, ax = plt.subplots(figsize=(max(6, df_raw[id_col].nunique()*0.4), 4))
        vc.plot(kind='bar', ax=ax, color=sns.color_palette('muted', df_raw[id_col].nunique()))
        ax.set_title(f"Readings per '{id_col}'")
        ax.set_ylabel('Count')
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f'{int(x):,}'))
        plt.tight_layout()
        safe = id_col.replace('/',' ').replace(' ','_')
        plt.savefig(DOCS_DIR/f'fig_readings_per_{safe}.png', dpi=120)
        plt.close()
        print(f"  Saved: docs/fig_readings_per_{safe}.png")

# Store key values for data_profile.md
print("\n\n=== ALL STATS COLLECTED ===")
print(f"FILE={CSV_PATH.name}")
print(f"ACTUAL_ROWS={actual_rows}")
print(f"DELTA={delta}")
print(f"COLUMNS={list(df_raw.columns)}")
print(f"DTYPES_DICT={df_raw.dtypes.astype(str).to_dict()}")
print(f"TS_COL={ts_col}")
print(f"IN_OUT_COL={in_out_col}")
print(f"TEMP_COL={temp_col}")
print(f"ID_COL={id_col}")
print(f"DATE_MIN={df['ts_parsed'].min()}")
print(f"DATE_MAX={df['ts_parsed'].max()}")
print(f"SPAN={span}")
print(f"GAP_MEDIAN_S={gaps_all.median():.2f}")
print(f"GAP_MEAN_S={gaps_all.mean():.2f}")
print(f"GAP_STD_S={gaps_all.std():.2f}")
print(f"GAP_MIN_S={gaps_all.min():.2f}")
print(f"GAP_MAX_S={gaps_all.max():.2f}")
print(f"COV={cv:.4f}")
print(f"VERDICT={verdict}")
print(f"TOTAL_MV={total_mv}")
print(f"N_DUPS={n_dups}")
print(f"TEMP_MIN={t.min():.4f}")
print(f"TEMP_MEAN={t.mean():.4f}")
print(f"TEMP_MEDIAN={t.median():.4f}")
print(f"TEMP_STD={t.std():.4f}")
print(f"TEMP_MAX={t.max():.4f}")
print(f"TEMP_BELOW_NEG50={(t < -50).sum()}")
print(f"TEMP_ABOVE_100={(t > 100).sum()}")
print(f"TEMP_EQ_NEG99={(t == -99).sum()}")
print(f"TEMP_EQ_999={(t == 999).sum()}")
print(f"TEMP_EQ_0={(t == 0).sum()}")
if in_out_col:
    vc2 = df_raw[in_out_col].value_counts(dropna=False)
    print(f"INOUT_DIST={vc2.to_dict()}")
if id_col:
    vc3 = df_raw[id_col].value_counts()
    print(f"ID_N_UNIQUE={df_raw[id_col].nunique()}")
    print(f"ID_MIN_READINGS={vc3.min()}")
    print(f"ID_MAX_READINGS={vc3.max()}")
    print(f"ID_MEAN_READINGS={vc3.mean():.1f}")
