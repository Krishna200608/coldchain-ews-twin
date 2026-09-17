"""
Re-run sampling interval analysis with correct date parsing (dayfirst=True).
Also per-tag (Out/In) interval analysis since room_id is degenerate.
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import pathlib

sns.set_theme(style='whitegrid', palette='muted')
REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
DOCS_DIR  = REPO_ROOT / 'docs'

df = pd.read_csv(REPO_ROOT / 'data' / 'raw' / 'IOT-temp.csv')
df['ts'] = pd.to_datetime(df['noted_date'], dayfirst=True, errors='coerce')

print(f'Rows total        : {len(df):,}')
print(f'ts parse failures : {df["ts"].isna().sum():,}')
print(f'Date min  : {df["ts"].min()}')
print(f'Date max  : {df["ts"].max()}')
span = df['ts'].max() - df['ts'].min()
print(f'Span      : {span}')

# ── Overall sampling intervals (correct parse) ─────────────────────────────
df_s = df.sort_values('ts').reset_index(drop=True)
gaps = df_s['ts'].diff().dt.total_seconds().dropna()

print('\n=== CORRECTED SAMPLING INTERVALS (dayfirst=True) ===')
print(f'n_gaps    : {len(gaps):,}')
print(f'min   (s) : {gaps.min():.1f}')
print(f'median(s) : {gaps.median():.1f}   ({gaps.median()/60:.4f} min)')
print(f'mean  (s) : {gaps.mean():.2f}   ({gaps.mean()/60:.4f} min)')
print(f'std   (s) : {gaps.std():.2f}')
print(f'max   (s) : {gaps.max():.1f}   ({gaps.max()/3600:.2f} h)')
cv = gaps.std() / gaps.mean()
print(f'CoV       : {cv:.4f}')
print(f'p25   (s) : {gaps.quantile(0.25):.1f}')
print(f'p75   (s) : {gaps.quantile(0.75):.1f}')
print(f'p95   (s) : {gaps.quantile(0.95):.1f}   ({gaps.quantile(0.95)/60:.1f} min)')
print(f'p99   (s) : {gaps.quantile(0.99):.1f}   ({gaps.quantile(0.99)/60:.1f} min)')

# Zero-gap count
n_zero = (gaps == 0).sum()
print(f'Zero gaps : {n_zero:,}  ({100*n_zero/len(gaps):.2f}%)  -- same-minute duplicates')
n_neg = (gaps < 0).sum()
print(f'Neg  gaps : {n_neg:,}  (timestamp ordering anomalies)')

# ── Per tag (Out/In) ──────────────────────────────────────────────────────
print('\n=== PER out/in TAG SAMPLING INTERVALS ===')
for tag, gdf in df_s.groupby('out/in'):
    gdf2 = gdf.sort_values('ts')
    g = gdf2['ts'].diff().dt.total_seconds().dropna()
    print(f'\n  Tag={tag!r}  n_readings={len(gdf):,}  n_gaps={len(g):,}')
    print(f'    min    (s) : {g.min():.1f}')
    print(f'    median (s) : {g.median():.1f}   ({g.median()/60:.4f} min)')
    print(f'    mean   (s) : {g.mean():.2f}   ({g.mean()/60:.4f} min)')
    print(f'    std    (s) : {g.std():.2f}')
    print(f'    max    (s) : {g.max():.1f}   ({g.max()/3600:.2f} h)')
    g_cv = g.std() / g.mean() if g.mean() != 0 else float('nan')
    print(f'    CoV        : {g_cv:.4f}')
    print(f'    zero gaps  : {(g==0).sum():,}')

# ── Histogram ──────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(12, 4))
nonzero = gaps[gaps > 0]
axes[0].hist(nonzero / 60, bins=100, color='steelblue', edgecolor='none', alpha=0.85)
axes[0].set_title('Inter-reading gaps (excl. zero-gaps) — full range')
axes[0].set_xlabel('Gap (minutes)')
axes[0].set_ylabel('Count')
p95 = float(nonzero.quantile(0.95))
zoomed = nonzero[nonzero <= p95]
axes[1].hist(zoomed / 60, bins=100, color='darkorange', edgecolor='none', alpha=0.85)
axes[1].set_title(f'Gaps zoomed to p95 ({p95/60:.1f} min)')
axes[1].set_xlabel('Gap (minutes)')
axes[1].set_ylabel('Count')
plt.tight_layout()
plt.savefig(DOCS_DIR / 'fig_sampling_intervals_corrected.png', dpi=120)
plt.close()
print('\nSaved: docs/fig_sampling_intervals_corrected.png')

# ── Temp distribution by tag ────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 4))
for tag, gdf in df.groupby('out/in'):
    ax.hist(gdf['temp'], bins=40, alpha=0.6, label=tag, edgecolor='none')
ax.set_title("Temperature distribution by Out/In tag")
ax.set_xlabel("Temperature (°C, proxy)")
ax.set_ylabel("Count")
ax.legend()
plt.tight_layout()
plt.savefig(DOCS_DIR / 'fig_temp_by_tag.png', dpi=120)
plt.close()
print('Saved: docs/fig_temp_by_tag.png')

print('\n=== FINAL KEY NUMBERS ===')
print(f'CORRECTED_GAP_MEDIAN_S={gaps.median():.2f}')
print(f'CORRECTED_GAP_MEAN_S={gaps.mean():.2f}')
print(f'CORRECTED_GAP_STD_S={gaps.std():.2f}')
print(f'CORRECTED_GAP_MAX_S={gaps.max():.1f}')
print(f'CORRECTED_COV={cv:.4f}')
print(f'ZERO_GAPS={n_zero}')
print(f'DATE_MIN={df["ts"].min()}')
print(f'DATE_MAX={df["ts"].max()}')
