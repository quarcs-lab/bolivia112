---
jupytext:
  cell_metadata_filter: -_sphinx_cell_id
  formats: ipynb,md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.19.1
kernelspec:
  display_name: bolivia112
  language: python
  name: python3
---

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/quarcs-lab/bolivia112/blob/main/notebooks/eda.ipynb)

# Exploratory Data Analysis (EDA)

An interactive tutorial for exploring regional development patterns across Bolivia's 112 provinces. This notebook covers descriptive statistics, regional comparisons, and the relationship between population, nighttime lights, and development. Province values are population-weighted aggregations of the underlying municipal data (intensive variables = weighted mean, extensive variables = sum); see [../province_aggregation_report.md](../province_aggregation_report.md) for the aggregation methodology.

## Setup

```{code-cell} ipython3
# Install packages not included in Google Colab's default environment.
# When running locally with UV, these are already installed and this cell is harmless.
!pip install contextily -q
```

```{code-cell} ipython3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import plotly.express as px
import plotly.graph_objects as go

import geopandas as gpd
import contextily as cx

import warnings
warnings.filterwarnings('ignore')
```

## Import data

```{code-cell} ipython3
# Province boundaries (geometry + metadata: prov_id, prov, dep, dep_id, shapeName, COORD_X, COORD_Y)
mapURL = 'https://raw.githubusercontent.com/quarcs-lab/bolivia112/main/maps/bolivia112provincesOpt.geojson'
gdf_map = gpd.read_file(mapURL)

# Province-level master table (population-weighted aggregations of the municipal data)
dataURL = 'https://raw.githubusercontent.com/quarcs-lab/bolivia112/main/bolivia112_v20260622.csv'
df = pd.read_csv(dataURL)

# Merge data onto geometry using the province join key (prov_id)
gdf = gdf_map.merge(df.drop(columns=['prov', 'dep', 'dep_id']), on='prov_id', how='left')
gdf.head(3)
```

```{code-cell} ipython3
dataDefinitions = pd.read_csv('https://raw.githubusercontent.com/quarcs-lab/bolivia112/main/definitions_bolivia112_v20260622.csv')
data_dict = dict(zip(dataDefinitions['varname'], dataDefinitions['varlabel']))
dataDefinitions
```

## Define key parameters

```{code-cell} ipython3
INDICATOR1 = 'imds'                # Sustainable Development Index
INDICATOR2 = 'pop2017'             # Population (2017)
INDICATOR3 = 'ln_t400NTLpc2017'    # Log nighttime lights per capita (2017)
INDICATOR4 = 'rank_imds'           # IMDS ranking

ADM1 = 'dep'                       # Department (9 departments)
ADM2 = 'prov'                      # Province (112 provinces)
```

## Descriptive statistics

- What do we know about the centrality and dispersion of our development indicator?

```{code-cell} ipython3
gdf[[INDICATOR1, INDICATOR2, INDICATOR3, INDICATOR4]].describe().round(2)
```

```{code-cell} ipython3
gdf[[ADM1, INDICATOR1]].groupby('dep').describe().round(2)
```

## Regional development differences

- How is our development indicator distributed across the 112 provinces and 9 departments of Bolivia?

```{code-cell} ipython3
px.strip(
    gdf,
    x=INDICATOR1,
    y=ADM1,
    color=ADM1,
    hover_name=ADM2,
    hover_data=[ADM1, INDICATOR4],
    labels=dict(data_dict)
)
```

```{code-cell} ipython3
px.histogram(
    gdf,
    x=INDICATOR1,
    color=ADM1,
    hover_name=ADM2,
    marginal='rug',
    hover_data=[ADM1, INDICATOR4],
    labels=dict(data_dict)
)
```

```{code-cell} ipython3
px.box(
    gdf,
    x=INDICATOR1,
    y=ADM1,
    color=ADM1,
    hover_name=ADM2,
    hover_data=[ADM1, INDICATOR4],
    labels=dict(data_dict)
)
```

## Population and development

- Do the most populous regions tend to be more developed?

```{code-cell} ipython3
px.bar(
    gdf.sort_values(by=INDICATOR2, ascending=True),
    x=ADM2,
    y=INDICATOR2,
    log_y=False,
    hover_data=[INDICATOR1, INDICATOR2, INDICATOR4],
    labels=dict(data_dict)
)
```

```{code-cell} ipython3
px.treemap(
    gdf,
    color=INDICATOR1,
    values=INDICATOR2,
    path=[ADM1, ADM2],
    hover_name=ADM2,
    hover_data=[INDICATOR4],
    labels=dict(data_dict)
)
```

```{code-cell} ipython3
px.sunburst(
    gdf,
    color=INDICATOR1,
    values=INDICATOR2,
    path=[ADM1, ADM2],
    hover_name=ADM2,
    hover_data=[INDICATOR4],
    labels=dict(data_dict)
)
```

```{code-cell} ipython3
px.scatter(
    gdf,
    x=INDICATOR2,
    log_x=True,
    y=INDICATOR1,
    color=ADM1,
    symbol=ADM1,
    hover_name=ADM2,
    trendline='ols',
    hover_data=[INDICATOR4],
    labels=dict(data_dict)
)
```

## Nighttime lights and development

- Can nighttime lights help us predict regional development?

```{code-cell} ipython3
gdf.explore(
    column=INDICATOR1,
    tooltip=[ADM1, ADM2, INDICATOR1, INDICATOR4],
    k=3,
    scheme='FisherJenks',
    cmap='BuPu',
    legend=True,
    tiles=cx.providers.NASAGIBS.ViirsEarthAtNight2012,
    style_kwds=dict(color="gray", weight=0.4, alpha=0.9),
    legend_kwds=dict(colorbar=False)
)
```

```{code-cell} ipython3
px.scatter(
    gdf,
    x=INDICATOR3,
    y=INDICATOR1,
    color=ADM1,
    symbol=ADM1,
    hover_name=ADM2,
    trendline='ols',
    trendline_scope='overall',
    hover_data=[INDICATOR3],
    labels=dict(data_dict)
)
```

- How heterogeneous is the relationship between regional development and nighttime lights?

```{code-cell} ipython3
px.scatter(
    gdf,
    x=INDICATOR3,
    y=INDICATOR1,
    color=ADM1,
    symbol=ADM1,
    hover_name=ADM2,
    trendline='ols',
    marginal_x="box",
    marginal_y="box",
    hover_data=[INDICATOR4],
    labels=dict(data_dict)
)
```
