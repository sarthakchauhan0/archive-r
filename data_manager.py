import polars as pl
import streamlit as st
import os

# Historical Events Registry
HISTORICAL_EVENTS = {
    1917: {365: "Russian Revolution: State Atheism rises in USSR"},
    1947: {750: "Partition of India", 770: "Creation of Pakistan"},
    1979: {630: "Iranian Revolution: Rise of Islamic Republic"},
    1991: {365: "Fall of USSR: Religious resurgence begins"},
    2011: {0: "Pew Projection Window Begins"}
}

@st.cache_data
def load_and_optimize_data(file_path, metadata_path='country_metadata.csv'):
    """Loads the dataset using Polars and joins with dynamic metadata."""
    if not os.path.exists(file_path):
        return None
    
    # Load Main Data
    df = pl.read_csv(file_path)
    
    # Load Metadata (CCode -> ISO, Region)
    if os.path.exists(metadata_path):
        meta_df = pl.read_csv(metadata_path)
        # Drop country_name from meta_df if it exists to avoid duplication with main df
        meta_df = meta_df.drop("country_name")
        df = df.join(meta_df, on="ccode", how="left")
    else:
        # Fallback if metadata missing
        df = df.with_columns([
            pl.col("ccode").replace(REGION_MAP, default="Others").alias("region"),
            pl.lit("UNK").alias("iso_alpha")
        ])
    
    # Cast types for efficiency
    df = df.with_columns([
        pl.col("ccode").cast(pl.Int32),
        pl.col("year").cast(pl.Int32),
        pl.col("percentage").cast(pl.Float32)
    ])
    
    return df

def get_filtered_data(df, regions=None, countries=None, year_range=(1816, 2026)):
    """Filters the dataset based on user selection."""
    filtered_df = df.filter(
        (pl.col("year") >= year_range[0]) & 
        (pl.col("year") <= year_range[1])
    )
    
    if regions:
        filtered_df = filtered_df.filter(pl.col("region").is_in(regions))
        
    if countries:
        filtered_df = filtered_df.filter(pl.col("country_name").is_in(countries))
        
    return filtered_df

def calculate_growth_metrics(df):
    """Calculates YoY change and total growth rate for each religion."""
    if df.is_empty():
        return pl.DataFrame(), pl.DataFrame()

    df = df.sort(["ccode", "religion_name", "year"])
    
    metrics_df = df.with_columns([
        pl.col("percentage").diff().over(["ccode", "religion_name"]).alias("yoy_change")
    ])
    
    # Total Growth Rate
    growth_df = metrics_df.group_by(["ccode", "religion_name"]).agg([
        (pl.col("percentage").last() - pl.col("percentage").first()).alias("total_growth")
    ])
    
    return metrics_df, growth_df

def get_secularized_count(df):
    """Counts countries where Unaffiliated share > 50% in the latest year of view."""
    if df.is_empty():
        return 0
    latest_year = df["year"].max()
    secular = df.filter(
        (pl.col("year") == latest_year) & 
        (pl.col("religion_name") == "Unaffiliated") & 
        (pl.col("percentage") > 50)
    )
    return secular["ccode"].n_unique()

def get_historical_events(ccodes, start_year, end_year):
    """Returns a list of events relevant to the current selection."""
    relevant_events = []
    for year, events in HISTORICAL_EVENTS.items():
        if start_year <= year <= end_year:
            for ccode, text in events.items():
                if ccode in ccodes or ccode == 0: 
                    relevant_events.append({"year": year, "text": text, "ccode": ccode})
    return relevant_events
