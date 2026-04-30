import pandas as pd
import country_converter as coco

cc = coco.CountryConverter()

df = pd.read_csv('country_metadata.csv')

def get_full_name(iso):
    if iso == 'UNK':
        return 'Unknown Territory'
    try:
        # Convert ISO3 to Full Name
        name = cc.convert(names=iso, to='name_short')
        if name == 'not found':
            return iso
        return name
    except:
        return iso

print("Converting ISO codes to full names...")
df['full_name'] = df['iso_alpha'].apply(get_full_name)

# Create the display label: "United States (USA)"
df['display_name'] = df.apply(lambda x: f"{x['full_name']} ({x['iso_alpha']})" if x['iso_alpha'] != 'UNK' else x['country_name'], axis=1)

df.to_csv('country_metadata.csv', index=False)
print("Updated country_metadata.csv with display_name column.")
print(df[['country_name', 'display_name']].head())
