# Geospatial Datasets

## Overview

This directory is designated for geospatial datasets in various GIS formats (GeoJSON, Shapefile, GeoPackage, etc.) covering Bolivia's 112 provinces. Currently, the main geospatial data is stored in the [maps/](../maps/) directory.

> **Note:** Province values are population-weighted aggregations of the municipal data (see [../province_aggregation_report.md](../province_aggregation_report.md)).

## Current Status

This directory is currently empty. Geospatial files are located in:

- **[maps/](../maps/)** - Contains province boundary files in GeoJSON format

## Planned Content

Future geospatial datasets may include:

- Raster layers (land cover, elevation, climate)
- Point datasets (infrastructure, facilities, landmarks)
- Additional administrative boundaries (departments, municipalities)
- Derived spatial products (buffers, centroids, grids)

## Working with Geospatial Data

For spatial analysis using this repository's data, refer to:

- **Boundary files**: [maps/bolivia112provincesOpt.geojson](../maps/bolivia112provincesOpt.geojson) - Optimized province boundaries
- **Full boundaries**: [maps/bolivia112provincesFull.geojson](../maps/bolivia112provincesFull.geojson) - Full-resolution boundaries
- **Python notebooks**: [notebooks/](../notebooks/) - Examples of spatial analysis
- **Interactive apps**: [apps/](../apps/) - Web-based visualization

## Loading Spatial Data

You can run the examples below in [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/notebooks/empty.ipynb)

```python
import geopandas as gpd

# Load province boundaries
url = "https://raw.githubusercontent.com/quarcs-lab/bolivia112/main/maps/bolivia112provincesOpt.geojson"
gdf = gpd.read_file(url)

# Join with attribute data
import pandas as pd
df_sdg = pd.read_csv("sdg/sdg.csv")
gdf = gdf.merge(df_sdg, on='prov_id', how='inner')

# Create choropleth map
gdf.plot(column='index_sdg1', legend=True)
```

## Coordinate Reference System

All spatial data in this repository uses:
- **CRS**: EPSG:4326 (WGS 84)
- **Units**: Decimal degrees

## Boundary File Properties

The province boundary GeoJSON files expose the following properties: `prov_id` (3-digit INE province code, e.g. 405=Litoral), `prov` (province name), `dep` (department), `dep_id` (department id), `shapeName`, `COORD_X`, and `COORD_Y` (centroid coordinates). There are 112 province features (versus 339 municipalities in the source dataset). Municipal-only id columns (`poly_id`, `asdf_id`, `mun_id`, `shapeID`, `dep_mun`) are not present.

## Join Key

Use `prov_id` to join spatial data with attribute datasets in this repository.
