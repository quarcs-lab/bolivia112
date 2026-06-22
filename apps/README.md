# Interactive Applications

## Overview

This directory contains interactive web applications built with Google Earth Engine (GEE) for visualizing spatial and temporal dynamics of development indicators across Bolivia's provinces.

**Note:** Province values are population-weighted means for intensive variables (SDGs by `pop2020`; others by year-matched `pop`) and sums for extensive ones; GDP is attached as-is from the GADM GeoPackage. See the dataset summary in the [main README](../README.md) and the full [province aggregation report](../province_aggregation_report.md).

## Applications

### GeoExplorer v1.0 - Bolivia

**Live Application:** [GeoExplorer: Population, Night-time Lights, Land Cover, and GDP](https://carlos-mendez.projects.earthengine.app/view/geoexplorer1v100bolivia)

An interactive dashboard for exploring space-time dynamics of key development indicators across Bolivia's 112 provinces.

**Features:**

- **Multi-layer Visualization**: Switch between population density, night-time lights, land cover, and GDP estimates
- **Temporal Comparison**: Compare data between 2013 and 2019 to track changes
- **Interactive Map**: Pan, zoom, and click on provinces to view detailed statistics
- **Color-coded Indicators**: Choropleth maps showing spatial patterns and regional disparities
- **No Coding Required**: Fully interactive web interface accessible to non-programmers

**Datasets Visualized:**

- Population density (persons per km²)
- Night-time lights intensity (proxy for economic activity)
- Land cover classifications (urban, forest, agriculture, etc.)
- GDP estimates (economic output)

**Use Cases:**

- Identifying high-growth provinces
- Tracking urbanization patterns
- Analyzing spatial inequality
- Educational demonstrations
- Policy briefings and presentations

## Source Code

### geoexplorer1v100bolivia.js

The JavaScript source code for the GeoExplorer application. This code runs on Google Earth Engine and includes:

- Data loading from Earth Engine collections
- Provincial boundary overlay
- Interactive UI components (sliders, layer selectors, legends)
- Temporal filtering (2013-2019)
- Color palette definitions

**Technology Stack:**

- Google Earth Engine API
- Earth Engine Code Editor
- JavaScript
- GEE UI widgets

**Data Sources Used:**

- Population: WorldPop or similar gridded population datasets
- Night-time Lights: VIIRS or DMSP-OLS
- Land Cover: ESA WorldCover or similar
- GDP: Modeled estimates from satellite proxies
- Boundaries: Bolivia 112 provinces shapefile

## Running the Application

**Option 1: Live Web App (Recommended)**

Simply visit: [https://carlos-mendez.projects.earthengine.app/view/geoexplorer1v100bolivia](https://carlos-mendez.projects.earthengine.app/view/geoexplorer1v100bolivia)

**Option 2: Earth Engine Code Editor**

1. Copy the code from [geoexplorer1v100bolivia.js](geoexplorer1v100bolivia.js)
2. Open the [Google Earth Engine Code Editor](https://code.earthengine.google.com/)
3. Paste the code and click "Run"
4. Interact with the map in the right panel

**Note:** You need a Google Earth Engine account to run code in the Code Editor (free for research and education).

## Customization

To create your own version:

1. Modify the year range in the code
2. Add additional datasets or indicators
3. Change color palettes
4. Adjust provincial boundaries to other regions
5. Deploy as your own Earth Engine App

## Related Resources

- Main visualization link in the project README: [Interactive Geospatial Dashboards](../README.md#-interactive-geospatial-dashboards)
- Satellite data processing code: [code/](../code/)
- Jupyter notebooks for offline analysis: [notebooks/](../notebooks/)
