import pandas as pd
import os
import glob

def inspect_headers(file_path):
    """Reads the first few lines of a CSV/XLSX file and returns the headers."""
    if not os.path.exists(file_path):
        return None
    
    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path, nrows=0)
        elif file_path.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_path, nrows=0)
        else:
            return None
        return list(df.columns)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

def find_mapping(headers, dataset_name):
    """Heuristic mapping of headers to unified schema."""
    mapping = {
        'country_code': None,
        'year': None,
        'religions': {
            'Christian': None,
            'Muslim': None,
            'Hindu': None,
            'Buddhist': None,
            'Unaffiliated': None
        }
    }
    
    # Common patterns
    patterns = {
        'country_code': ['cow', 'ccode', 'iso', 'country code', 'state', 'cname'],
        'year': ['year', 'yr', 'time'],
        'Christian': ['chrst', 'christian', 'cath', 'prot', 'orth'],
        'Muslim': ['islm', 'muslim', 'sunni', 'shia'],
        'Hindu': ['hind', 'hindu'],
        'Buddhist': ['bud', 'buddhist', 'mah', 'thr'],
        'Unaffiliated': ['nonrelig', 'unaffiliated', 'no_rel', 'none', 'atheist']
    }
    
    for h in headers:
        h_lower = h.lower()
        
        # Match country code (prioritize 'cow' for CoW and 'iso' for Pew)
        if not mapping['country_code']:
            if any(p in h_lower for p in patterns['country_code']):
                mapping['country_code'] = h
        
        # Match year
        if not mapping['year']:
            if any(p in h_lower for p in patterns['year']):
                mapping['year'] = h
        
        # Match religions
        for relig, p_list in patterns.items():
            if relig in mapping['religions']:
                if any(p in h_lower for p in p_list):
                    # For some datasets, we might have multiple (e.g. prot, cath)
                    # For now, we just pick the first match or we'll need a list
                    if mapping['religions'][relig] is None:
                        mapping['religions'][relig] = h
                    else:
                        if isinstance(mapping['religions'][relig], list):
                            mapping['religions'][relig].append(h)
                        else:
                            mapping['religions'][relig] = [mapping['religions'][relig], h]

    return mapping

def main():
    data_dir = './data'
    # Potential file patterns based on user input
    files_to_check = {
        'CoW': '*wrp*',
        'QoG': '*qog*',
        'Pew': '*pew*'
    }
    
    print("=== Stage 1: Dataset Header Inspection ===\n")
    
    found_any = False
    for label, pattern in files_to_check.items():
        matches = glob.glob(os.path.join(data_dir, pattern), recursive=True)
        if not matches:
            # Also check root if not in data/
            matches = glob.glob(pattern, recursive=True)
            
        if matches:
            found_any = True
            for file_path in matches:
                print(f"Inspecting {label} dataset: {file_path}")
                headers = inspect_headers(file_path)
                if headers:
                    mapping = find_mapping(headers, label)
                    print(f"  Detected Country Code: {mapping['country_code']}")
                    print(f"  Detected Year: {mapping['year']}")
                    print("  Religious Percentage Columns:")
                    for relig, cols in mapping['religions'].items():
                        print(f"    - {relig}: {cols}")
                print("-" * 40)
        else:
            print(f"Dataset {label} not found (Pattern: {pattern})")

    if not found_any:
        print("\n[WARNING] No dataset files found. Please place them in the 'data/' directory.")
        print("Example Mapping (based on standard schemas):")
        print("""
| Dataset | Country Code | Year | Christian | Muslim | Hindu | Buddhist | Unaffiliated |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| CoW | cow | year | chrstpct | islmpct | hindpct | budpct | nonreligpct |
| QoG | ccodecow | year | re_religpct_chr | re_religpct_isl | re_religpct_hin | re_religpct_bud | re_religpct_not |
| Pew | Country Code | Year | Christians | Muslims | Hindus | Buddhists | Unaffiliated |
        """)

if __name__ == "__main__":
    main()
