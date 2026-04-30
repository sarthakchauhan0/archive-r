import pandas as pd
import polars as pl
import numpy as np
import os

def load_cow_data(file_path):
    """Loads and harmonizes CoW WRP data."""
    print(f"Processing CoW data: {file_path}")
    df = pd.read_csv(file_path)
    
    # Christian: sum of all Christian categories
    chr_cols = [c for c in df.columns if c.startswith('chrst') and c.endswith('pct')]
    isl_cols = [c for c in df.columns if c.startswith('islm') and c.endswith('pct')]
    bud_cols = [c for c in df.columns if c.startswith('bud') and c.endswith('pct')]
    
    df['Christian'] = df[chr_cols].sum(axis=1)
    df['Muslim'] = df[isl_cols].sum(axis=1)
    df['Hindu'] = df['hindgenpct']
    df['Buddhist'] = df[bud_cols].sum(axis=1)
    df['Unaffiliated'] = df['nonreligpct']
    
    # Keep only necessary columns
    df_clean = df[['state', 'year', 'Christian', 'Muslim', 'Hindu', 'Buddhist', 'Unaffiliated', 'name']].copy()
    df_clean.rename(columns={'state': 'ccode', 'name': 'country_name'}, inplace=True)
    
    return df_clean

def load_pew_data(file_path, country_to_ccode):
    """Loads and harmonizes Pew Projections data."""
    print(f"Processing Pew data: {file_path}")
    df = pd.read_excel(file_path)
    
    # Clean non-numeric values in religion columns
    religions_cols = ['Christians', 'Muslims', 'Hindus', 'Buddhists', 'Religiously_unaffiliated', 'Population']
    for col in religions_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Normalize by population
    rel_map = {
        'Christians': 'Christian',
        'Muslims': 'Muslim',
        'Hindus': 'Hindu',
        'Buddhists': 'Buddhist',
        'Religiously_unaffiliated': 'Unaffiliated'
    }
    
    for pew_col, our_col in rel_map.items():
        # Avoid division by zero
        df[our_col] = np.where(df['Population'] > 0, df[pew_col] / df['Population'], 0)
        
    df.rename(columns={'Year': 'year', 'Country': 'country_name'}, inplace=True)
    
    # Map country name to ccode
    df['ccode'] = df['country_name'].map(country_to_ccode).fillna(-1)
    
    return df[['ccode', 'year', 'Christian', 'Muslim', 'Hindu', 'Buddhist', 'Unaffiliated', 'country_name']]

def main():
    data_dir = 'data'
    cow_file = os.path.join(data_dir, 'WRP_national.csv')
    pew_file = os.path.join(data_dir, 'Pew_GRF_Projections.xlsx')
    
    if not os.path.exists(cow_file) or not os.path.exists(pew_file):
        print("Error: Required files missing.")
        return

    # 1. Load CoW and build name mapping
    df_cow = load_cow_data(cow_file)
    
    # Build a robust mapping from name to ccode
    # Some names might change slightly, but this is a good start
    country_to_ccode = df_cow.groupby('country_name')['ccode'].first().to_dict()
    # Add some common manual overrides if needed
    country_to_ccode.update({
        'United States': 2,
        'United Kingdom': 200,
        'Russia': 365,
        'Vietnam': 816,
        'Tanzania': 510
    })
    
    # 2. Load Pew
    df_pew = load_pew_data(pew_file, country_to_ccode)
    
    # 3. Combine
    df_combined = pd.concat([
        df_cow[df_cow['year'] <= 2010],
        df_pew[df_pew['year'] > 2010]
    ], ignore_index=True)
    
    # 4. Interpolation
    print("Interpolating missing annual values...")
    df_melted = df_combined.melt(id_vars=['ccode', 'year', 'country_name'], 
                                var_name='religion_name', value_name='percentage')
    
    full_years = pd.DataFrame({'year': range(1816, 2027)})
    
    final_rows = []
    # Filter out unmapped countries or those with too little data
    for (ccode, rel), group in df_melted.groupby(['ccode', 'religion_name']):
        if ccode == -1 or group['percentage'].isna().all():
            continue
            
        group = group.sort_values('year').drop_duplicates('year')
        
        # Merge with full years
        group_full = full_years.merge(group, on='year', how='left')
        group_full['ccode'] = ccode
        group_full['religion_name'] = rel
        group_full['country_name'] = group['country_name'].iloc[0]
        
        # Interpolate
        group_full['percentage'] = group_full['percentage'].interpolate(method='linear', limit_direction='both')
        final_rows.append(group_full)
    
    if not final_rows:
        print("Error: No data to process after filtering.")
        return
        
    df_final = pd.concat(final_rows)
    
    # 5. Normalization (Ensure total = 100)
    print("Normalizing religious shares to 100%...")
    sums = df_final.groupby(['ccode', 'year'])['percentage'].transform('sum')
    df_final['percentage'] = np.where(sums > 0, (df_final['percentage'] / sums) * 100, 0)
    
    # 6. Generate Metadata Crosswalk
    print("Generating dynamic country metadata...")
    # COW to ISO3 to Region mapping for common states
    # This acts as the source of truth for the dashboard
    cow_crosswalk = {
        2: ('USA', 'Americas'), 20: ('CAN', 'Americas'), 70: ('MEX', 'Americas'),
        140: ('BRA', 'Americas'), 160: ('ARG', 'Americas'),
        200: ('GBR', 'Europe'), 210: ('NLD', 'Europe'), 220: ('FRA', 'Europe'),
        230: ('ESP', 'Europe'), 255: ('DEU', 'Europe'), 325: ('ITA', 'Europe'),
        365: ('RUS', 'Europe'), 390: ('DNK', 'Europe'),
        432: ('MLI', 'Africa'), 510: ('TZA', 'Africa'), 530: ('ETH', 'Africa'),
        630: ('IRN', 'Middle East'), 640: ('TUR', 'Middle East'), 666: ('ISR', 'Middle East'),
        700: ('AFG', 'Asia'), 710: ('CHN', 'Asia'), 731: ('PRK', 'Asia'), 
        732: ('KOR', 'Asia'), 740: ('JPN', 'Asia'), 750: ('IND', 'Asia'), 
        770: ('PAK', 'Asia'), 800: ('THA', 'Asia'), 816: ('VNM', 'Asia'), 900: ('AUS', 'Asia')
    }
    
    metadata = df_final[['ccode', 'country_name']].drop_duplicates()
    metadata['iso_alpha'] = metadata['ccode'].map(lambda x: cow_crosswalk.get(int(x), ('UNK', 'Other'))[0])
    metadata['region'] = metadata['ccode'].map(lambda x: cow_crosswalk.get(int(x), ('UNK', 'Other'))[1])
    
    metadata.to_csv('country_metadata.csv', index=False)
    
    # 7. Save Master CSV (Keep it lean, join with metadata in app)
    output_file = 'global_religion_timeseries_1816_2026.csv'
    df_final.to_csv(output_file, index=False)
    print(f"Success! Master CSV and Metadata generated.")

if __name__ == "__main__":
    main()
