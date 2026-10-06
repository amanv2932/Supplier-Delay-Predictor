import pandas as pd
import numpy as np

df = pd.read_csv('supplier_shipment_delay_dataset.csv')
df['origin_city'] = df['origin_city'].astype(str).str.strip()
df['destination_city'] = df['destination_city'].astype(str).str.strip()
df['transit_mode'] = df['transit_mode'].astype(str).str.strip()
df['delay_days'] = pd.to_numeric(df['delay_days'], errors='coerce')

# RAW SHIPMENT LEVEL
print("RAW SHIPMENT LEVEL")
print(f"Minimum: {df['delay_days'].min()}")
print(f"Maximum: {df['delay_days'].max()}")
print(f"Mean: {df['delay_days'].mean()}")
print(f"Median: {df['delay_days'].median()}")
print(f"Negative records: {(df['delay_days'] < 0).sum()}")
print(f"Zero records: {(df['delay_days'] == 0).sum()}")
print(f"Positive records: {(df['delay_days'] > 0).sum()}")

# ROUTE LEVEL
print("\nROUTE LEVEL")
route_stats = df.groupby(['origin_city', 'destination_city']).agg(
    shipment_count=('delay_days', 'count'),
    avg_delay=('delay_days', 'mean'),
    delayed_rate=('delayed', lambda x: (x == 'Yes').sum() / len(x) * 100)
).reset_index()

print(f"Negative-average routes: {(route_stats['avg_delay'] < 0).sum()}")
print(f"Zero-average routes: {(route_stats['avg_delay'] == 0).sum()}")
print(f"Positive-average routes: {(route_stats['avg_delay'] > 0).sum()}")
print(f"Lowest route average: {route_stats['avg_delay'].min()}")
print(f"Highest route average: {route_stats['avg_delay'].max()}")
print(f"Average of route averages: {route_stats['avg_delay'].mean()}")

# CURRENT ROUTE
print("\nCURRENT ROUTE")
curr = df[(df['transit_mode'] == 'Road') & (df['origin_city'] == 'Ahmedabad') & (df['destination_city'] == 'Visakhapatnam')]
print(f"Route: Ahmedabad to Visakhapatnam (Road)")
print(f"Shipment count: {len(curr)}")
if len(curr) > 0:
    print(f"Average delay: {curr['delay_days'].mean()}")
    print(f"Minimum delay: {curr['delay_days'].min()}")
    print(f"Maximum delay: {curr['delay_days'].max()}")
    print(f"Median delay: {curr['delay_days'].median()}")
    print(f"Negative shipment count: {(curr['delay_days'] < 0).sum()}")
    print(f"Zero shipment count: {(curr['delay_days'] == 0).sum()}")
    print(f"Positive shipment count: {(curr['delay_days'] > 0).sum()}")
    print(f"Delayed rate: {(curr['delayed'] == 'Yes').sum() / len(curr) * 100}%")

print("\nTOP 10 LOWEST AVERAGE DELAY ROUTES")
print(route_stats.sort_values(by='avg_delay').head(10).to_string())

print("\nTOP 10 HIGHEST AVERAGE DELAY ROUTES")
print(route_stats.sort_values(by='avg_delay', ascending=False).head(10).to_string())
