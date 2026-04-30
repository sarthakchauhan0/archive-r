import streamlit as st
import data_manager
import ai_analyst
import plotly.express as px
import plotly.graph_objects as go
import polars as pl
import os

# 1. Page Configuration & Architectural CSS
st.set_page_config(page_title="Religious Evolution: Portfolio Edition", layout="wide")

# Architectural Palette
SOFT_DARK = "transparent"
ACCENT_LIGHT = "inherit"
BORDER_COLOR = "rgba(128, 128, 128, 0.2)"

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
    }}
    
    /* Card Styles: Semi-transparent to adapt to background */
    .card-container {{
        border: 1px solid {BORDER_COLOR};
        padding: 24px;
        border-radius: 4px;
        background-color: rgba(128, 128, 128, 0.05);
        margin-bottom: 20px;
    }}

    .ai-report-card {{
        background: rgba(128, 128, 128, 0.08);
        border: 1px solid {BORDER_COLOR};
        border-radius: 4px;
        padding: 20px 24px;
        font-size: 0.95rem;
        line-height: 1.75;
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
    }}
    
    /* Sidebar Legibility Fix */
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] .stCaption {{
        color: #FFFFFF !important;
    }}
    
    [data-testid="stSidebar"] .stMarkdown p em {{
        color: #CCCCCC !important;
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

# 2.5 Load Metadata for UI Display Names
@st.cache_data
def load_metadata():
    if os.path.exists("country_metadata.csv"):
        return pl.read_csv("country_metadata.csv")
    return None

df_meta = load_metadata()
# Fallback if no display_name yet: use country_name
if df_meta is not None and "display_name" not in df_meta.columns:
    df_meta = df_meta.with_columns(pl.col("country_name").alias("display_name"))

# 3. Sidebar & Navigation
with st.sidebar:
    st.markdown("# ARCHIVE-R")
    st.markdown("*A Global Religion Time-Series Exploration*")
    st.markdown("---")
    
    compare_mode = st.toggle("Enable Comparison Mode", value=False)
    
    # Use session state to persist selections across reruns
    if 'selected_regions' not in st.session_state:
        all_avail_regions = df_master["region"].unique().to_list()
        target_defaults = ["America", "Europe"]
        st.session_state.selected_regions = [r for r in target_defaults if r in all_avail_regions]
        if not st.session_state.selected_regions:
            st.session_state.selected_regions = all_avail_regions
    
    regions = st.multiselect("Regions", 
                            options=sorted(df_master["region"].unique().to_list()), 
                            key='selected_regions')
    
    # Filter countries based on region and map to display names
    if df_meta is not None:
        filtered_meta = df_meta.filter(pl.col("region").is_in(regions))
        display_to_code = dict(zip(filtered_meta["display_name"], filtered_meta["country_name"]))
        code_to_display = dict(zip(filtered_meta["country_name"], filtered_meta["display_name"]))
        available_display_names = sorted(filtered_meta["display_name"].to_list())
    else:
        # Fallback
        available_codes = sorted(df_master.filter(pl.col("region").is_in(regions))["country_name"].unique().to_list())
        display_to_code = {c: c for c in available_codes}
        code_to_display = {c: c for c in available_codes}
        available_display_names = available_codes

    if compare_mode:
        st.subheader("Select Comparison")
        disp_a = st.selectbox("Country A", options=available_display_names, index=0)
        disp_b = st.selectbox("Country B", options=available_display_names, index=1 if len(available_display_names) > 1 else 0)
        selected_countries = [display_to_code[disp_a], display_to_code[disp_b]]
    else:
        # For multiselect, we need to handle the conversion
        current_codes = df_master.filter(pl.col("region").is_in(regions))["country_name"].unique().to_list()
        # User requested defaults: USA, UK (UKG), France (FRN)
        default_codes = [c for c in ["USA", "UKG", "FRN"] if c in current_codes]
        
        if not default_codes:
            default_codes = current_codes[:3]
            
        default_displays = [code_to_display[c] for c in default_codes if c in code_to_display]

        if 'selected_displays' not in st.session_state:
            st.session_state.selected_displays = default_displays
            
        selected_displays = st.multiselect("Focus Countries", 
                                          options=available_display_names,
                                          key='selected_displays')
        selected_countries = [display_to_code[d] for d in selected_displays]
    
    year_range = st.slider("Timeline", 1816, 2026, (1926, 2026))

    st.markdown("---")
    st.caption("⚠️ **Data Disclaimer**: Global religious demographics for years post-2010 may be incomplete or modeled, as national census updates often take 10+ years to fully aggregate and verify.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style='font-size:0.7rem; color:#666; line-height:1.4;'>
    <b>RESEARCH NOTICE & LIMITATION OF LIABILITY</b><br>
    This platform is a research experiment. Data is aggregated from external repositories (CoW, Pew Research, etc.) and all narrative analysis is generated by an AI model (Gemini). 
    The developer assumes no responsibility for any inaccuracies, interpretations, or consequences arising from the use of this information.
    </div>
    """, unsafe_allow_html=True)

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
        # Define country names for UI and AI
        country_a, country_b = disp_a, disp_b
        
        st.subheader("COMPARATIVE OVERLAYS")
        # Line Chart for Comparison
        compare_data = filtered_df.to_pandas()
        fig_compare = px.line(compare_data, x="year", y="percentage", color="religion_name", 
                              line_dash="country_name",
                              color_discrete_map=RELIGION_PALETTE,
                              title=f"{country_a} (Solid) vs {country_b} (Dashed)")
        fig_compare.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", 
            paper_bgcolor="rgba(0,0,0,0)", 
            height=500,
            font=dict(color="#888")
        )
        st.plotly_chart(fig_compare, use_container_width=True)

        # AI Comparison Tools
        st.markdown("<hr style='border-color:#333'>", unsafe_allow_html=True)
        
        # Safety check: Compare mode works best with exactly two countries
        num_selected = len(selected_countries)
        if num_selected != 2:
            st.warning("⚠️ Comparison analysis requires exactly two countries to be selected in the sidebar.")
            st.button("↗ ANALYSE COMPARISON", disabled=True, use_container_width=True)
        else:
            c1, c2 = st.columns(2)
            with c1:
                if st.button(f"↗ STRUCTURAL ANALYSIS", use_container_width=True):
                    st.markdown("<p style='font-size:0.75rem;letter-spacing:0.15em;color:#888;'>AI STRUCTURAL COMPARISON</p>", unsafe_allow_html=True)
                    with st.spinner("Generating comparative analysis…"):
                        stats_a = ai_analyst.extract_country_stats(compare_data, country_a)
                        stats_b = ai_analyst.extract_country_stats(compare_data, country_b)
                        report = ai_analyst.generate_comparison_report(country_a, country_b, stats_a, stats_b)
                    st.markdown(f"<div class='ai-report-card'>{report}</div>", unsafe_allow_html=True)

            with c2:
                if st.button(f"↗ SOCIOECONOMIC CONTRAST", use_container_width=True):
                    # Use 1990-2026 as default for impact analysis
                    analysis_start = year_range[0]
                    analysis_end = year_range[1]
                    if analysis_start == 1816 and analysis_end == 2026:
                        analysis_start = 1990

                    with st.spinner(f"Comparing socioeconomic impacts for {country_a} vs {country_b}…"):
                        data_a = compare_data[(compare_data['year'] >= analysis_start) & (compare_data['year'] <= analysis_end)]
                        stats_a = ai_analyst.extract_country_stats(data_a, country_a)
                        stats_b = ai_analyst.extract_country_stats(data_a, country_b)
                        comp_impact = ai_analyst.generate_comparative_impact_analysis(country_a, country_b, analysis_start, analysis_end, stats_a, stats_b)
                    
                    st.markdown("<p style='font-size:0.75rem;letter-spacing:0.15em;color:#888;'>AI COMPARATIVE SOCIOECONOMIC IMPACT</p>", unsafe_allow_html=True)
                    st.markdown(f"<div class='ai-report-card'>{comp_impact}</div>", unsafe_allow_html=True)

    else:
        st.subheader("EVOLUTIONARY TRAJECTORY")
        timeline_data = filtered_df.to_pandas()
        fig_timeline = px.area(timeline_data, x="year", y="percentage", color="religion_name", 
                               line_group="country_name",
                               color_discrete_map=RELIGION_PALETTE)
        
        # Annotations
        ccodes = filtered_df["ccode"].unique().to_list()
        events = data_manager.get_historical_events(ccodes, year_range[0], year_range[1])
        for ev in events:
            fig_timeline.add_annotation(x=ev["year"], y=0.9, text=ev["text"], showarrow=False, bgcolor="rgba(128,128,128,0.2)", bordercolor="rgba(128,128,128,0.2)", font=dict(size=9))
            
        fig_timeline.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", 
            paper_bgcolor="rgba(0,0,0,0)", 
            height=500, 
            yaxis_range=[0, 100],
            font=dict(color="#888")
        )
        st.plotly_chart(fig_timeline, use_container_width=True)

        # AI Impact Analysis Button
        st.markdown("<hr style='border-color:#333'>", unsafe_allow_html=True)
        
        # Logic for single country vs multiple countries
        num_selected = len(selected_countries)
        if num_selected == 0:
            st.info("Select a country in the sidebar to run an impact analysis.")
        elif num_selected > 1:
            st.warning("⚠️ Impact analysis is optimized for single-country studies. Please select only one country or enable 'Comparison Mode' in the sidebar.")
            st.button("↗ ANALYSE IMPACT", disabled=True, use_container_width=True)
        else:
            target_country = selected_countries[0]
            if st.button(f"↗ ANALYSE IMPACT FOR {target_country.upper()}", use_container_width=True):
                # Use 1926-2026 as default for analysis
                analysis_start = year_range[0]
                analysis_end = year_range[1]
                if analysis_start == 1816 and analysis_end == 2026:
                    analysis_start = 1926
                    st.info(f"Note: Using the 1990–2026 window for more accurate socioeconomic analysis.")

                with st.spinner(f"Analysing socioeconomic impact for {target_country}…"):
                    analysis_data = timeline_data[(timeline_data['year'] >= analysis_start) & (timeline_data['year'] <= analysis_end)]
                    stats = ai_analyst.extract_country_stats(analysis_data, target_country)
                    impact = ai_analyst.generate_impact_analysis(target_country, analysis_start, analysis_end, stats)
                    
                st.markdown("<p style='font-size:0.75rem;letter-spacing:0.15em;color:#888;'>AI SOCIOECONOMIC IMPACT ANALYSIS</p>", unsafe_allow_html=True)
                st.markdown(f"<div class='ai-report-card'>{impact}</div>", unsafe_allow_html=True)

with c_side:
    st.subheader("Insights")
    
    # Generate dynamic architectural insight
    if not filtered_df.is_empty():
        top_religions = filtered_df.group_by("religion_name").agg(pl.col("percentage").mean()).sort("percentage", descending=True).head(2)
        rel1 = top_religions.row(0)[0]
        rel2 = top_religions.row(1)[0] if top_religions.height > 1 else None
        
        color_labels = {
            "Christian": "Sage",
            "Muslim": "Steel Blue",
            "Hindu": "Dusty Rose",
            "Buddhist": "Muted Gold",
            "Unaffiliated": "Slate Gray",
            "Others": "Warm Charcoal"
        }
        
        label1 = color_labels.get(rel1, "Primary Tone")
        label2 = color_labels.get(rel2, "Secondary Tone") if rel2 else ""
        
        region_text = f"across {', '.join(regions)}" if len(regions) < 3 else "across the selected territories"
        
        if rel2:
            insight_text = f"Observe how the {label1} ({rel1}) and {label2} ({rel2}) interact {region_text}."
        else:
            insight_text = f"Observe the dominance of the {label1} ({rel1}) {region_text}."
    else:
        insight_text = "Select regions to begin the architectural analysis."

    st.markdown(f"""
    <div style='font-size: 0.9rem; color: #888; border-left: 2px solid #444; padding-left: 15px;'>
    The architectural transition of belief systems often follows economic industrialization.
    <br><br>
    {insight_text}
    </div>
    """, unsafe_allow_html=True)
    if not growth_df.is_empty() and df_meta is not None:
        # Cast ccode to Int64 to ensure join compatibility
        g_df = growth_df.with_columns(pl.col("ccode").cast(pl.Int64))
        m_df = df_meta.select(["ccode", "display_name"]).with_columns(pl.col("ccode").cast(pl.Int64))
        
        # Join with metadata to get display_name
        enriched_growth = g_df.join(m_df, on="ccode")
        
        st.dataframe(
            enriched_growth.to_pandas().drop("ccode", axis=1), 
            use_container_width=True, 
            hide_index=True,
            column_config={
                "display_name": "Country",
                "religion_name": "Religion",
                "total_growth": st.column_config.NumberColumn(
                    "Growth (%)",
                    help="Total percentage point change over the selected period",
                    format="%.1f%%"
                )
            }
        )

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
