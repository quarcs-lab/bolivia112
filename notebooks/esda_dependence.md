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
  display_name: Python 3
  language: python
  name: python3
---

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/quarcs-lab/bolivia112/blob/main/notebooks/esda_dependence.ipynb)

# Spatial Distribution and Dependence

An interactive tutorial exploring how Bolivia's Sustainable Development Index (IMDS) is spatially distributed across 112 provinces. This notebook covers map classification schemes, spatial weights, global and local measures of spatial autocorrelation (Moran's I, LISA). Province values are population-weighted aggregations of the underlying municipal data (intensive variables = weighted mean, extensive variables = sum); see [../province_aggregation_report.md](../province_aggregation_report.md).

## Setup

```{code-cell} ipython3
# Install packages not included in Google Colab's default environment.
# When running locally with UV, these are already installed and this cell is harmless.
!pip install contextily libpysal esda splot mapclassify -q
```

```{code-cell} ipython3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import plotly.express as px

import geopandas as gpd
import contextily as cx
import mapclassify as mc

from libpysal import weights
from esda.moran import Moran, Moran_Local
from splot.esda import moran_scatterplot, lisa_cluster
from splot.libpysal import plot_spatial_weights

import warnings
warnings.filterwarnings('ignore')
```

## Import data

```{code-cell} ipython3
# Province boundaries (112 provinces) and the population-weighted province dataset,
# merged on prov_id (3-digit INE province code).
mapURL = 'https://raw.githubusercontent.com/quarcs-lab/bolivia112/main/maps/bolivia112provincesOpt.geojson'
dataURL = 'https://raw.githubusercontent.com/quarcs-lab/bolivia112/main/bolivia112_v20260622.csv'

gmap = gpd.read_file(mapURL)
data = pd.read_csv(dataURL)

gdf = gmap.merge(data, on='prov_id', how='left', suffixes=('', '_data'))
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

## Spatial distribution

### Box-plot breaks

```{code-cell} ipython3
px.box(
    gdf,
    x=INDICATOR1,
    hover_name=ADM2,
    hover_data=[INDICATOR4, ADM1],
    labels=dict(data_dict)
)
```

```{code-cell} ipython3
gdf.explore(
    column=INDICATOR1,
    tooltip=[ADM1, ADM2, INDICATOR1, INDICATOR4],
    scheme='BoxPlot',
    k=6,
    cmap='coolwarm',
    legend=True,
    tiles='CartoDB positron',
    style_kwds=dict(color="gray", weight=0.4),
    legend_kwds=dict(colorbar=False)
)
```

```{code-cell} ipython3
mc.BoxPlot(gdf[INDICATOR1])
```

```{code-cell} ipython3
fig, ax = plt.subplots(figsize=(9, 6))

gdf.plot(
    column=INDICATOR1,
    scheme='BoxPlot',
    cmap='coolwarm',
    edgecolor='k',
    linewidth=0.5,
    alpha=0.8,
    legend=True,
    ax=ax,
    legend_kwds={'bbox_to_anchor': (1.00, 0.92)}
)

cx.add_basemap(ax, crs=gdf.crs.to_string(), source=cx.providers.CartoDB.Positron, attribution=False)
plt.title('Spatial distribution: Box-plot breaks')
plt.tight_layout()
ax.axis("off")
plt.show()
```

### Fisher-Jenks breaks

```{code-cell} ipython3
gdf.explore(
    column=INDICATOR1,
    tooltip=[ADM1, ADM2, INDICATOR1, INDICATOR4],
    k=3,
    scheme='FisherJenks',
    cmap='coolwarm',
    legend=True,
    tiles='CartoDB positron',
    style_kwds=dict(color="gray", weight=0.4),
    legend_kwds=dict(colorbar=False)
)
```

```{code-cell} ipython3
mc.FisherJenks(gdf[INDICATOR1], k=3)
```

```{code-cell} ipython3
fig, ax = plt.subplots(figsize=(9, 6))

gdf.plot(
    column=INDICATOR1,
    scheme='FisherJenks',
    k=3,
    cmap='coolwarm',
    edgecolor='k',
    linewidth=0.5,
    alpha=0.8,
    legend=True,
    ax=ax,
    legend_kwds={'bbox_to_anchor': (1.00, 0.92)}
)

cx.add_basemap(ax, crs=gdf.crs.to_string(), source=cx.providers.CartoDB.Positron, attribution=False)
plt.title('Spatial distribution: Three natural breaks')
plt.tight_layout()
ax.axis("off")
plt.show()
```

## Spatial dependence

- To what extent is the performance of a region similar to that of its neighbours?
- To what extent is there an overall pattern of "clustering"?
- Where can we find statistically significant spatial clusters?
- Where can we find statistically significant spatial outliers?

### Spatial connectivity

```{code-cell} ipython3
W = weights.KNN.from_dataframe(gdf, k=6)
W.transform = 'r'

plot_spatial_weights(W, gdf)
```

### Global dependence

```{code-cell} ipython3
df_MORAN = gdf[[ADM1, ADM2, INDICATOR1]].copy()
df_MORAN["WxINDICATOR1"] = weights.lag_spatial(W, df_MORAN[INDICATOR1])
```

```{code-cell} ipython3
px.scatter(
    df_MORAN,
    x=INDICATOR1,
    y="WxINDICATOR1",
    hover_name=ADM2,
    hover_data=[ADM1, INDICATOR1, 'WxINDICATOR1'],
    trendline="ols",
    marginal_x="box",
    marginal_y="box",
    labels=dict(data_dict)
)
```

### Local dependence

```{code-cell} ipython3
globalMoran = Moran(gdf[INDICATOR1], W)
MoranI = "{:.2f}".format(globalMoran.I)

localMoran = Moran_Local(gdf[INDICATOR1], W, permutations=999, seed=12345)
```

```{code-cell} ipython3
fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(12, 5))

moran_scatterplot(localMoran, p=0.10, aspect_equal=False, zstandard=False, ax=axes[0])
lisa_cluster(localMoran, gdf, p=0.10, legend_kwds={'bbox_to_anchor': (0.02, 0.90)}, ax=axes[1])

axes[0].set_xlabel('Indicator')
axes[0].set_ylabel('Spatial lag of indicator')
axes[0].set_title(f"(a) Moran scatterplot (Moran's I = {MoranI})")
axes[1].set_title("(b) Spatial clusters and outliers (p < 0.10)")

plt.show()
```
