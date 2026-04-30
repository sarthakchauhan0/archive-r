# ARCHIVE-R: A Structural Study of Global Belief

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![Polars](https://img.shields.io/badge/Polars-Fast-orange.svg)

**ARCHIVE-R** is a high-end, research-grade analytical dashboard designed to visualize the evolution and structural shifts of global religions from 1816 to 2026. Built with a sleek, architectural "Editorial Noir" aesthetic, it processes over two centuries of historical data to track the trajectories of major belief systems across 200 nations.

## Features

- **Evolutionary Trajectories**: Interactive, stacked area timelines displaying market share shifts of major religions (Christianity, Islam, Hinduism, Buddhism, Unaffiliated) over 210 years.
- **Comparative Overlays**: Select any two countries to instantly compare their structural religious evolution side-by-side.
- **Spatial Migration Map**: An animated decadal choropleth map that visually tracks the geographic spread and shifting dominance of belief systems.
- **Dynamic Metrics**: Real-time calculations of the fastest-growing and steepest-declining belief systems based on dynamic user filtering.
- **High-Performance Pipeline**: Data is ingested, interpolated, and normalized using a lightning-fast `Polars` backend.

## Architecture

The project seamlessly stitches together three distinct datasets to create a continuous 210-year timeline:
1. **Correlates of War (CoW) WRP (1816–2010)**: Detailed historical composition.
2. **Pew Research GRF Projections (2011–2026)**: Modern demographics and near-future trends.

*Note: The Quality of Government (QoG) standard dataset was audited during development, but CoW provided a more comprehensive continuous timeline for this specific analysis.*

## Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/sarthakchauhan0/archive-r.git
   cd archive-r
   ```

2. **Install dependencies:**
   Ensure you have Python installed, then run:
   ```bash
   pip install streamlit pandas polars plotly openpyxl
   ```

3. **Generate the Master Dataset (Optional if CSV already present):**
   If you need to regenerate the underlying data from the raw sources:
   ```bash
   python3 stitching_pipeline.py
   ```

4. **Launch the Dashboard:**
   ```bash
   streamlit run app.py
   ```

## Design Philosophy

ARCHIVE-R departs from standard generic data visualization platforms by employing a strict, high-contrast, minimalist design language. 
- **Typography**: Clean, sans-serif fonts for optimal readability.
- **Color Palette**: Desaturated tones (Sage, Steel Blue, Dusty Rose, Muted Gold, Slate Gray) replace garish primaries to reflect the serious, historical nature of the data.
- **Layout**: Architectural grid systems enforce order and focus on the data.

## Author

**Sarthak Chauhan**
