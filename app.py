import streamlit as st
import data_manager
import plotly.express as px
import plotly.graph_objects as go
import polars as pl

# 1. Page Configuration & Architectural CSS
st.set_page_config(page_title="Religious Evolution: Portfolio Edition", layout="wide")

# Architectural Palette
SOFT_DARK = "#1A1A1B"
ACCENT_LIGHT = "#E4E4E4"
BORDER_COLOR = "#333333"

# Desaturated Religion Palette
RELIGION_PALETTE = {
    "Christian": "#8A9A5B",  # Sage
    "Muslim": "#6D8299",     # Steel Blue
    "Hindu": "#B48484",      # Dusty Rose
    "Buddhist": "#D4AF37",   # Muted Gold
    "Unaffiliated": "#A9A9A9" # Slate Gray
}

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;700&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Outfit', sans-serif;
        background-color: {SOFT_DARK};
        color: {ACCENT_LIGHT};
    }}
    
    .stApp {{
        background-color: {SOFT_DARK};
    }}
    
    .card-container {{
        border: 1px solid {BORDER_COLOR};
        padding: 24px;
        border-radius: 4px;
        background-color: #212122;
        margin-bottom: 20px;
    }}
    
    .metric-label {{
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #888;
        margin-bottom: 4px;
    }}
    
    .metric-value {{
        font-size: 1.8rem;
        font-weight: 700;
        color: {ACCENT_LIGHT};
    }}
    
    h1 {{
        font-size: 3.5rem !important;
        font-weight: 700 !important;
        letter-spacing: -0.06em !important;
        margin-bottom: 0px !important;
    }}
    
    .stSidebar {{
        background-color: #121213 !important;
        border-right: 1px solid {BORDER_COLOR};
    }}
    </style>
""", unsafe_allow_html=True)

# 2. Data Initialization
DATA_PATH = 'global_religion_timeseries_1816_2026.csv'
df_master = data_manager.load_and_optimize_data(DATA_PATH)

if df_master is None:
    st.error("Dataset not found.")
    st.stop()

# 3. Sidebar & Navigation
with st.sidebar:
    st.markdown("# ARCHIVE-R")
    st.markdown("*A Global Religion Time-Series Exploration*")
    st.markdown("---")
    
    compare_mode = st.toggle("Enable Comparison Mode", value=False)
    
    # Use session state to persist selections across reruns
    if 'selected_regions' not in st.session_state:
        st.session_state.selected_regions = df_master["region"].unique().to_list()
    
    regions = st.multiselect("Regions", 
                            options=df_master["region"].unique().to_list(), 
                            key='selected_regions')
    
    all_countries = df_master.filter(pl.col("region").is_in(regions))["country_name"].unique().to_list()
    
    if compare_mode:
        st.subheader("Select Comparison")
        country_a = st.selectbox("Country A", options=all_countries, index=0)
        country_b = st.selectbox("Country B", options=all_countries, index=1 if len(all_countries) > 1 else 0)
        selected_countries = [country_a, country_b]
    else:
        if 'selected_countries' not in st.session_state:
            st.session_state.selected_countries = all_countries[:3]
            
        # Ensure selected countries are still in the valid options (post-region filter)
        valid_selection = [c for c in st.session_state.selected_countries if c in all_countries]
        
        selected_countries = st.multiselect("Focus Countries", 
                                            options=all_countries, 
                                            key='selected_countries')
    
    year_range = st.slider("Timeline", 1816, 2026, (1816, 2026))

# 4. Filter Logic
filtered_df = data_manager.get_filtered_data(df_master, regions, selected_countries, year_range)
metrics_df, growth_df = data_manager.calculate_growth_metrics(filtered_df)

# 5. Header Grid (Architectural Style)
st.markdown("<h1>STRUCTURAL BELIEF</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='color: #888; margin-bottom: 40px;'>AN ANALYSIS OF RELIGIOUS SHIFTS | {year_range[0]} – {year_range[1]}</p>", unsafe_allow_html=True)

if not growth_df.is_empty():
    k1, k2, k3 = st.columns(3)
    
    kpi1 = growth_df.sort("total_growth", descending=True).row(0)
    kpi2 = growth_df.sort("total_growth", descending=False).row(0)
    kpi3 = data_manager.get_secularized_count(filtered_df)
    
    with k1:
        st.markdown(f"<div class='card-container'><div class='metric-label'>Rise</div><div class='metric-value'>{kpi1[1]}</div><div style='color: #4CAF50'>+{kpi1[2]:.1f}%</div></div>", unsafe_allow_html=True)
    with k2:
        st.markdown(f"<div class='card-container'><div class='metric-label'>Fall</div><div class='metric-value'>{kpi2[1]}</div><div style='color: #F44336'>{kpi2[2]:.1f}%</div></div>", unsafe_allow_html=True)
    with k3:
        st.markdown(f"<div class='card-container'><div class='metric-label'>Secularization</div><div class='metric-value'>{kpi3} Nations</div><div style='color: #888'>> 50% Threshold</div></div>", unsafe_allow_html=True)

# 6. Main Visual: Portfolio Grid
st.markdown("---")
c_main, c_side = st.columns([3, 1])

with c_main:
    if compare_mode:
        st.subheader("COMPARATIVE OVERLAYS")
        # Line Chart for Comparison
        compare_data = filtered_df.to_pandas()
        fig_compare = px.line(compare_data, x="year", y="percentage", color="religion_name", 
                              line_dash="country_name",
                              color_discrete_map=RELIGION_PALETTE,
                              template="plotly_dark",
                              title=f"{country_a} (Solid) vs {country_b} (Dashed)")
        fig_compare.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", height=500)
        st.plotly_chart(fig_compare, use_container_width=True)
    else:
        st.subheader("EVOLUTIONARY TRAJECTORY")
        timeline_data = filtered_df.to_pandas()
        fig_timeline = px.area(timeline_data, x="year", y="percentage", color="religion_name", 
                               line_group="country_name",
                               color_discrete_map=RELIGION_PALETTE,
                               template="plotly_dark")
        
        # Annotations
        ccodes = filtered_df["ccode"].unique().to_list()
        events = data_manager.get_historical_events(ccodes, year_range[0], year_range[1])
        for ev in events:
            fig_timeline.add_annotation(x=ev["year"], y=0.9, text=ev["text"], showarrow=False, bgcolor="#333", bordercolor="#555", font=dict(size=9))
            
        fig_timeline.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", height=500, yaxis_range=[0, 100])
        st.plotly_chart(fig_timeline, use_container_width=True)

with c_side:
    st.subheader("Insights")
    st.markdown("""
    <div style='font-size: 0.9rem; color: #888; border-left: 2px solid #444; padding-left: 15px;'>
    The architectural transition of belief systems often follows economic industrialization.
    <br><br>
    Observe how the desaturated Sage (Christianity) and Steel Blue (Islam) interact in the Global South.
    </div>
    """, unsafe_allow_html=True)
    if not growth_df.is_empty():
        st.dataframe(growth_df.to_pandas().drop("ccode", axis=1), use_container_width=True, hide_index=True)

# 7. Animated Map (Lower Grid)
st.markdown("---")
st.subheader("Spatial Migration of Belief")

# Map respects the selected countries/regions, but falls back to global if no ISO-mappable countries exist
map_data = filtered_df.filter(pl.col("iso_alpha").is_not_null() & (pl.col("iso_alpha") != "UNK")).to_pandas()

if map_data.empty:
    # Fallback: show the full global map when the selection has no mappable ISO codes
    st.caption("⚠️ The selected region/countries have no mappable ISO codes — showing global view instead.")
    map_data = df_master.filter(pl.col("iso_alpha").is_not_null() & (pl.col("iso_alpha") != "UNK")).to_pandas()

map_data['decade'] = (map_data['year'] // 10) * 10
map_decade = map_data.groupby(['iso_alpha', 'decade', 'religion_name'])['percentage'].mean().reset_index()
map_decade = map_decade.sort_values('decade')

fig_map = px.choropleth(map_decade, 
                        locations="iso_alpha", 
                        color="percentage", 
                        animation_frame="decade",
                        category_orders={"decade": sorted(map_decade['decade'].unique())},
                        color_continuous_scale="Greys", 
                        range_color=[0, 100],
                        template="plotly_dark")
fig_map.update_geos(
    visible=True,
    resolution=50,
    showcoastlines=True, coastlinecolor="Grey",
    showland=True, landcolor="#1A1A1B",
    showocean=True, oceancolor="#0E1117",
    showlakes=True, lakecolor="#0E1117",
    showcountries=True, countrycolor="#444"
)
fig_map.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", height=700)
st.plotly_chart(fig_map, use_container_width=True)

st.markdown("<p style='text-align: center; color: #444;'>ARCHIVE-R | A STRUCTURAL STUDY | 2026</p>", unsafe_allow_html=True)
