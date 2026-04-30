import pandas as pd
import numpy as np
import os

def generate_mock_data():
    data_dir = './data'
    os.makedirs(data_dir, exist_ok=True)

    # 1. Mock CoW Data (5-year intervals, 1816-1945)
    years_cow = list(range(1816, 1946, 5))
    cow_data = []
    countries = [
        {'cow': 800, 'name': 'Thailand', 'religion': 'Buddhist'},
        {'cow': 200, 'name': 'UK', 'religion': 'Christian'},
        {'cow': 2, 'name': 'USA', 'religion': 'Christian'},
        {'cow': 220, 'name': 'France', 'religion': 'Christian'},
        {'cow': 255, 'name': 'Germany', 'religion': 'Christian'},
        {'cow': 750, 'name': 'India', 'religion': 'Hindu'}
    ]
    
    for y in years_cow:
        for c in countries:
            if c['religion'] == 'Christian':
                cow_data.append({'cow': c['cow'], 'year': y, 'chrstpct': 0.85, 'islmpct': 0.01, 'hindpct': 0.0, 'budpct': 0.0, 'nonreligpct': 0.14})
            elif c['religion'] == 'Buddhist':
                cow_data.append({'cow': c['cow'], 'year': y, 'chrstpct': 0.01, 'islmpct': 0.05, 'hindpct': 0.0, 'budpct': 0.90, 'nonreligpct': 0.04})
            elif c['religion'] == 'Hindu':
                cow_data.append({'cow': c['cow'], 'year': y, 'chrstpct': 0.01, 'islmpct': 0.15, 'hindpct': 0.80, 'budpct': 0.0, 'nonreligpct': 0.04})
    pd.DataFrame(cow_data).to_csv(os.path.join(data_dir, 'WRP_national.csv'), index=False)

    # 2. Mock QoG Data (Annual, 1946-2010)
    years_qog = list(range(1946, 2011))
    qog_data = []
    for y in years_qog:
        for c in countries:
            if c['religion'] == 'Christian':
                qog_data.append({'ccodecow': c['cow'], 'year': y, 're_religpct_chr': 70.0, 're_religpct_isl': 3.0, 're_religpct_hin': 1.0, 're_religpct_bud': 0.5, 're_religpct_not': 25.5})
            elif c['religion'] == 'Buddhist':
                qog_data.append({'ccodecow': c['cow'], 'year': y, 're_religpct_chr': 1.0, 're_religpct_isl': 5.0, 're_religpct_hin': 0.0, 're_religpct_bud': 90.0, 're_religpct_not': 4.0})
            elif c['religion'] == 'Hindu':
                qog_data.append({'ccodecow': c['cow'], 'year': y, 're_religpct_chr': 1.0, 're_religpct_isl': 15.0, 're_religpct_hin': 80.0, 're_religpct_bud': 0.0, 're_religpct_not': 4.0})
    pd.DataFrame(qog_data).to_csv(os.path.join(data_dir, 'qog_std_ts_jan24.csv'), index=False)

    # 3. Mock Pew Data (2011-2026)
    years_pew = list(range(2011, 2027))
    pew_data = []
    iso_map = {800: 'THA', 200: 'GBR', 2: 'USA', 220: 'FRA', 255: 'DEU', 750: 'IND'}
    for y in years_pew:
        for c in countries:
            iso = iso_map[c['cow']]
            if c['religion'] == 'Christian':
                pew_data.append({'Country Code': iso, 'Year': y, 'Christians': 55.0, 'Muslims': 8.0, 'Hindus': 2.0, 'Buddhists': 1.0, 'Unaffiliated': 34.0})
            elif c['religion'] == 'Buddhist':
                pew_data.append({'Country Code': iso, 'Year': y, 'Christians': 1.2, 'Muslims': 5.5, 'Hindus': 0.1, 'Buddhists': 89.0, 'Unaffiliated': 4.2})
            elif c['religion'] == 'Hindu':
                pew_data.append({'Country Code': iso, 'Year': y, 'Christians': 1.5, 'Muslims': 16.0, 'Hindus': 78.0, 'Buddhists': 0.5, 'Unaffiliated': 4.0})
    pd.DataFrame(pew_data).to_csv(os.path.join(data_dir, 'Pew_GRF_Projections.csv'), index=False)

    print("Mock data generated in ./data/")

if __name__ == "__main__":
    generate_mock_data()
