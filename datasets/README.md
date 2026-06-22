# Datasets

## Overview

This directory contains merged datasets that combine multiple data sources for comprehensive spatial analysis of Bolivia's provinces.

> **Note:** Province values are population-weighted aggregations of the underlying municipal data (intensive variables = weighted mean, extensive variables = sum). See [../province_aggregation_report.md](../province_aggregation_report.md) for details.

## Files

### sdgs_satelliteEmbeddings2017.csv

A comprehensive dataset merging socio-economic indicators (SDGs) with satellite-derived features for 2017, covering Bolivia's 112 provinces. This is the primary analytical dataset for machine learning and spatial econometric studies.

## Variable Dictionary

| Variable Name | Description |
|---------------|-------------|
| **prov_id** | Unique province identifier (3-digit INE code, e.g. 405=Litoral); primary join key |
| **prov** | Province name |
| **dep** | Department name |
| **dep_id** | Department ID code |
| **dep_prov** | Combined department-province identifier |
| **imds** | Provincial Sustainable Development Index (composite indicator) |
| **index_sdg1** | SDG 1 Index: No Poverty |
| **index_sdg2** | SDG 2 Index: Zero Hunger |
| **index_sdg3** | SDG 3 Index: Good Health and Well-being |
| **index_sdg4** | SDG 4 Index: Quality Education |
| **index_sdg5** | SDG 5 Index: Gender Equality |
| **index_sdg6** | SDG 6 Index: Clean Water and Sanitation |
| **index_sdg7** | SDG 7 Index: Affordable and Clean Energy |
| **index_sdg8** | SDG 8 Index: Decent Work and Economic Growth |
| **index_sdg9** | SDG 9 Index: Industry, Innovation and Infrastructure |
| **index_sdg10** | SDG 10 Index: Reduced Inequalities |
| **index_sdg11** | SDG 11 Index: Sustainable Cities and Communities |
| **index_sdg13** | SDG 13 Index: Climate Action |
| **index_sdg15** | SDG 15 Index: Life on Land |
| **index_sdg16** | SDG 16 Index: Peace, Justice and Strong Institutions |
| **index_sdg17** | SDG 17 Index: Partnerships for the Goals |
| **A00-A63** | Satellite embedding dimensions (64 features): High-dimensional feature vectors extracted from satellite imagery using deep learning. These capture visual patterns like texture, building density, vegetation, and land use. See [satelliteEmbeddings/README.md](../satelliteEmbeddings/README.md) for details. |

## Usage

This merged dataset is ready for:
- **Machine Learning**: Predicting SDG indicators from satellite embeddings
- **Spatial Analysis**: Exploring relationships between development and visual landscape patterns
- **Dimensionality Reduction**: Applying PCA to the 64 embedding dimensions
- **Clustering**: Identifying provinces with similar characteristics

## Example Code

You can run the examples below in [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/notebooks/empty.ipynb)

```python
import pandas as pd

# Load the merged dataset
url = "https://raw.githubusercontent.com/quarcs-lab/bolivia112/main/datasets/sdgs_satelliteEmbeddings2017.csv"
df = pd.read_csv(url)

# Select embedding columns
embedding_cols = [f'A{str(i).zfill(2)}' for i in range(64)]
X = df[embedding_cols]

# Select target SDG variable
y = df['index_sdg1']  # No Poverty index

# Use for machine learning models

# Verify the dataset covers all 112 provinces (use prov_id as the join key)
assert df['prov_id'].nunique() == 112
```

## Data Sources

- **SDG Data**: [Atlas Municipal de los ODS Bolivia](https://atlas.sdsnbolivia.org), aggregated from 339 municipalities to 112 provinces using population weighting (see [../province_aggregation_report.md](../province_aggregation_report.md))
- **Satellite Embeddings**: Google Earth Engine Satellite Embeddings V1
- **Administrative Boundaries**: Bolivia 112 provinces shapefile

## Join Key

Use `prov_id` to join this dataset with other datasets in the repository.
