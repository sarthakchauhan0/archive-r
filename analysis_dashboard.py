import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

def analyze_trends(df):
    results = {}
    
    # 1. Fastest Decline (Top 5 countries/religions over 50-year window)
    print("\n[Analyzing Fastest Declines (50-year window)]...")
    declines = []
    # Pivot back to wide for easier rolling calculation
    wide_df = df.pivot(index=['ccode', 'year'], columns='religion_name', values='percentage').reset_index()
    
    for religion in df['religion_name'].unique():
        # Calculate 50-year change
        wide_df[f'{religion}_50yr_diff'] = wide_df.groupby('ccode')[religion].transform(lambda x: x.diff(50))
        
    # Melt diffs to find top declines
    diff_cols = [c for c in wide_df.columns if '_50yr_diff' in c]
    diff_df = wide_df.melt(id_vars=['ccode', 'year'], value_vars=diff_cols, var_name='religion_diff', value_name='change')
    
    # Negative change means decline. We want the most negative.
    top_declines = diff_df.sort_values('change').head(5)
    results['top_declines'] = top_declines
    
    # 2. Unaffiliated Takeover
    print("[Analyzing Unaffiliated Takeovers]...")
    # Find years where Unaffiliated is the max percentage
    wide_df['dominant_religion'] = wide_df[['Christian', 'Muslim', 'Hindu', 'Buddhist', 'Unaffiliated']].idxmax(axis=1)
    takeovers = wide_df[wide_df['dominant_religion'] == 'Unaffiliated'].copy()
    
    # Get the first year this happened for each country
    takeover_first = takeovers.sort_values('year').groupby('ccode').first().reset_index()
    results['takeovers'] = takeover_first[['ccode', 'year']]

    # 3. Data Jumps (> 15% YoY)
    print("[Detecting Data Jumps (>15%)]...")
    jumps = []
    for religion in ['Christian', 'Muslim', 'Hindu', 'Buddhist', 'Unaffiliated']:
        wide_df[f'{religion}_yoy'] = wide_df.groupby('ccode')[religion].diff().abs()
        jump_idx = wide_df[wide_df[f'{religion}_yoy'] > 0.15].index
        for idx in jump_idx:
            row = wide_df.loc[idx]
            label = "Dataset Transition Artifact" if row['year'] in [1946, 2011] else "Potential Historical Event"
            jumps.append({
                'ccode': row['ccode'],
                'year': row['year'],
                'religion': religion,
                'change': wide_df.loc[idx, f'{religion}_yoy'],
                'type': label
            })
    results['jumps'] = pd.DataFrame(jumps)
    
    return results

def plot_country_trends(df, target_ccode, output_html='country_trends.html'):
    country_data = df[df['ccode'] == target_ccode]
    if country_data.empty:
        print(f"No data found for ccode {target_ccode}")
        return

    fig = px.line(country_data, x="year", y="percentage", color="religion_name",
                  title=f"Religious Composition Over Time (ccode: {target_ccode})",
                  labels={"percentage": "Share (0.0 - 1.0)", "year": "Year", "religion_name": "Religion"},
                  template="plotly_dark")
    
    fig.update_layout(yaxis_range=[0, 1.05])
    fig.write_html(output_html)
    print(f"Chart saved to {output_html}")

def main():
    input_file = 'global_religion_timeseries_1816_2026.csv'
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found. Run the stitching pipeline first.")
        return
        
    df = pd.read_csv(input_file)
    
    # Run analysis
    results = analyze_trends(df)
    
    print("\n" + "="*30)
    print("TOP 5 FASTEST DECLINES (50-YEAR WINDOW)")
    print("="*30)
    print(results['top_declines'][['ccode', 'year', 'religion_diff', 'change']])
    
    print("\n" + "="*30)
    print("UNAFFILIATED TAKEOVERS (FIRST YEAR)")
    print("="*30)
    if results['takeovers'].empty:
        print("No takeovers detected in this dataset.")
    else:
        print(results['takeovers'])
        
    print("\n" + "="*30)
    print("DATA JUMPS DETECTED")
    print("="*30)
    if results['jumps'].empty:
        print("No jumps > 15% detected.")
    else:
        print(results['jumps'])

    # Visualization for ccode 200 (UK) - just as an example
    plot_country_trends(df, 200, 'uk_trends.html')
    plot_country_trends(df, 800, 'thailand_trends.html')

if __name__ == "__main__":
    main()
