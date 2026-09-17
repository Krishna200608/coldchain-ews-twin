"""Investigate timestamp parsing failures and the 'id' column structure."""
import pandas as pd
import numpy as np

df = pd.read_csv('data/raw/IOT-temp.csv')

print('=== TIMESTAMP PARSE FAILURE INVESTIGATION ===')
ts_coerce = pd.to_datetime(df['noted_date'], infer_datetime_format=True, errors='coerce')
bad_mask = ts_coerce.isna()
bad = df[bad_mask]['noted_date']
print(f'Total failures: {len(bad):,}')
print(f'Null in noted_date: {df["noted_date"].isna().sum()}')
print(f'Empty string      : {(df["noted_date"] == "").sum()}')
print()
print('Sample unparsed values (first 15):')
print(bad.head(15).tolist())
print()
print('Unique bad values (first 10):')
print(bad.drop_duplicates().head(10).tolist())
print()
print('Top-20 bad date values by frequency:')
print(bad.value_counts().head(20).to_string())

# Try alternative formats
print()
ts_m_d_y = pd.to_datetime(df['noted_date'], format='%m-%d-%Y %H:%M', errors='coerce')
print(f'format=%m-%d-%Y %H:%M  failures: {ts_m_d_y.isna().sum():,}')

ts_d_m_y = pd.to_datetime(df['noted_date'], format='%d-%m-%Y %H:%M', errors='coerce')
print(f'format=%d-%m-%Y %H:%M  failures: {ts_d_m_y.isna().sum():,}')

ts_mixed = pd.to_datetime(df['noted_date'], dayfirst=True, errors='coerce')
print(f'dayfirst=True          failures: {ts_mixed.isna().sum():,}')

# What proportion of 'Out' vs 'In' are in the bad set?
bad_outin = df[bad_mask]['out/in'].value_counts()
print()
print('out/in distribution among parse failures:')
print(bad_outin.to_string())

print()
print('=== ID COLUMN INVESTIGATION ===')
print(f'Unique id values    : {df["id"].nunique():,}')
print(f'Total rows          : {len(df):,}')
print(f'Are IDs row-unique? : {df["id"].nunique() == len(df)}')
print('Sample id values:')
print(df['id'].head(10).tolist())
print('id value pattern (common prefix?):')
# Check if all start with same prefix
sample = df['id'].dropna().head(100)
prefixes = sample.str[:5].value_counts()
print(prefixes.head(10).to_string())
