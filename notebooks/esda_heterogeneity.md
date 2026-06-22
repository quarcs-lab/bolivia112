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

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/quarcs-lab/bolivia112/blob/main/notebooks/esda_heterogeneity.ipynb)

# Spatial Heterogeneity (GWR & MGWR)

An interactive tutorial exploring how the relationship between nighttime lights and regional development varies across Bolivia's 112 provinces. This notebook covers Geographically Weighted Regression (GWR) and Multiscale GWR (MGWR) to detect spatially varying coefficients.

> The province-level data are population-weighted aggregations of the municipal DS4Bolivia data (intensive variables = weighted mean, extensive variables = sum). See [`../province_aggregation_report.md`](../province_aggregation_report.md) for the aggregation methodology.

## Setup

```{code-cell} ipython3
# Install packages not included in Google Colab's default environment.
# When running locally with UV, these are already installed and this cell is harmless.
!pip install contextily libpysal mgwr -q
```

```{code-cell} ipython3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import geopandas as gpd
import contextily as cx

from mgwr.gwr import GWR, MGWR
from mgwr.sel_bw import Sel_BW

import warnings
warnings.filterwarnings('ignore')
```

## Import data

```{code-cell} ipython3
# Province boundaries (geometry + centroid coordinates), keyed by prov_id
mapURL = 'https://raw.githubusercontent.com/quarcs-lab/bolivia112/main/maps/bolivia112provincesOpt.geojson'
prov_map = gpd.read_file(mapURL)

# Province-level master table (population-weighted aggregations), keyed by prov_id
dataURL = 'https://raw.githubusercontent.com/quarcs-lab/bolivia112/main/bolivia112_v20260622.csv'
prov_data = pd.read_csv(dataURL)

# Merge attributes onto the geometry on the province key (prov_id)
gdf = prov_map.merge(prov_data, on='prov_id', how='inner', suffixes=('', '_data'))
gdf.head(3)
```

```{code-cell} ipython3
dataDefinitions = pd.read_csv('https://raw.githubusercontent.com/quarcs-lab/bolivia112/main/definitions_bolivia112_v20260622.csv')
data_dict = dict(zip(dataDefinitions['varname'], dataDefinitions['varlabel']))
```

## Define key parameters

```{code-cell} ipython3
INDICATOR1 = 'imds'                # Sustainable Development Index (province-level)
INDICATOR3 = 'ln_t400NTLpc2017'    # Log nighttime lights per capita (2017)
INDICATOR4 = 'rank_imds'           # IMDS ranking

ADM1 = 'dep'                       # Department (9 departments)
ADM2 = 'prov'                      # Province (112 provinces)
```

## Prepare data for regression

```{code-cell} ipython3
y = gdf[INDICATOR1].values.reshape((-1, 1))
X = gdf[INDICATOR3].values.reshape((-1, 1))
coords = list(zip(gdf['COORD_X'], gdf['COORD_Y']))

print(f"y shape: {y.shape}, X shape: {X.shape}, coords: {len(coords)} points")
```

## GWR analysis

```{code-cell} ipython3
gwr_selector = Sel_BW(coords, y, X, spherical=True)
gwr_bw = gwr_selector.search(criterion='AICc')
print('GWR bandwidth =', gwr_bw)
```

```{code-cell} ipython3
gwr_results = GWR(coords, y, X, gwr_bw).fit()
gwr_results.summary()
```

```{code-cell} ipython3
gwr_bw_ci = gwr_results.get_bws_intervals(gwr_selector)
print(gwr_bw_ci)
```

```{code-cell} ipython3
print('Mean R2 =', gwr_results.R2)
print('AIC =',     gwr_results.aic)
print('AICc =',    gwr_results.aicc)
```

```{code-cell} ipython3
gdf['gwr_R2'] = gwr_results.localR2
```

```{code-cell} ipython3
gdf.explore(
    column='gwr_R2',
    tooltip=[ADM1, ADM2, 'gwr_R2', INDICATOR4, INDICATOR1, INDICATOR3],
    k=5,
    scheme='FisherJenks',
    cmap='coolwarm',
    legend=True,
    tiles='CartoDB dark_matter',
    style_kwds=dict(color="gray", weight=0.4),
    legend_kwds=dict(colorbar=False)
)
```

```{code-cell} ipython3
gdf['gwr_intercept'] = gwr_results.params[:, 0]
gdf['gwr_slope1'] = gwr_results.params[:, 1]

gwr_filtered_t1 = gwr_results.filter_tvals(alpha=0.05)
gwr_filtered_tc1 = gwr_results.filter_tvals()
```

```{code-cell} ipython3
gdf.explore(
    column='gwr_slope1',
    tooltip=[ADM1, ADM2, 'gwr_slope1', INDICATOR4, INDICATOR1, INDICATOR3],
    k=5,
    scheme='FisherJenks',
    cmap='coolwarm',
    legend=True,
    tiles='CartoDB dark_matter',
    style_kwds=dict(color="gray", weight=0.4),
    legend_kwds=dict(colorbar=False)
)
```

```{code-cell} ipython3
fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(18, 6))

gdf.plot(column='gwr_slope1', cmap='coolwarm', linewidth=0.01, scheme='FisherJenks', k=5,
         legend=True, legend_kwds={'bbox_to_anchor': (1.10, 0.96)}, ax=axes[0])
axes[0].set_title(f'(a) GWR: NTL (BW: {gwr_bw}), all coeffs', fontsize=12)
axes[0].axis("off")

gdf.plot(column='gwr_slope1', cmap='coolwarm', linewidth=0.05, scheme='FisherJenks', k=5,
         legend=False, ax=axes[1])
gdf[gwr_filtered_t1[:, 1] == 0].plot(color='white', linewidth=0.05, edgecolor='black', ax=axes[1])
axes[1].set_title(f'(b) GWR: NTL (BW: {gwr_bw}), significant coeffs', fontsize=12)
axes[1].axis("off")

gdf.plot(column='gwr_slope1', cmap='coolwarm', linewidth=0.05, scheme='FisherJenks', k=5,
         legend=False, ax=axes[2])
gdf[gwr_filtered_tc1[:, 1] == 0].plot(color='white', linewidth=0.05, edgecolor='black', ax=axes[2])
axes[2].set_title(f'(c) GWR: NTL (BW: {gwr_bw}), corrected p-values', fontsize=12)
axes[2].axis("off")

plt.tight_layout()
plt.show()
```

## MGWR analysis

```{code-cell} ipython3
Zy = (y - y.mean(axis=0)) / y.std(axis=0)
ZX = (X - X.mean(axis=0)) / X.std(axis=0)
```

```{code-cell} ipython3
mgwr_selector = Sel_BW(coords, Zy, ZX, multi=True, spherical=True)
mgwr_bw = mgwr_selector.search(criterion='AICc')
mgwr_bw
```

```{code-cell} ipython3
mgwr_results = MGWR(coords, Zy, ZX, mgwr_selector).fit()
mgwr_results.summary()
```

```{code-cell} ipython3
mgwr_bw_ci = mgwr_results.get_bws_intervals(mgwr_selector)
print(mgwr_bw_ci)
```

```{code-cell} ipython3
print('Mean R2 =', mgwr_results.R2)
print('AIC =',     mgwr_results.aic)
print('AICc =',    mgwr_results.aicc)
```

```{code-cell} ipython3
gdf['mgwr_intercept'] = mgwr_results.params[:, 0]
gdf['mgwr_slope1'] = mgwr_results.params[:, 1]

mgwr_filtered_t1 = mgwr_results.filter_tvals(alpha=0.05)
mgwr_filtered_tc1 = mgwr_results.filter_tvals()
```

```{code-cell} ipython3
gdf.explore(
    column='mgwr_slope1',
    tooltip=[ADM1, ADM2, 'mgwr_slope1', INDICATOR4, INDICATOR1, INDICATOR3],
    k=5,
    scheme='FisherJenks',
    cmap='coolwarm',
    legend=True,
    tiles='CartoDB dark_matter',
    style_kwds=dict(color="gray", weight=0.4),
    legend_kwds=dict(colorbar=False)
)
```

```{code-cell} ipython3
fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(18, 6))

gdf.plot(column='mgwr_slope1', cmap='coolwarm', linewidth=0.01, scheme='FisherJenks', k=5,
         legend=True, legend_kwds={'bbox_to_anchor': (1.10, 0.96)}, ax=axes[0])
axes[0].set_title(f'(a) MGWR: NTL (BW: {mgwr_bw}), all coeffs', fontsize=12)
axes[0].axis("off")

gdf.plot(column='mgwr_slope1', cmap='coolwarm', linewidth=0.05, scheme='FisherJenks', k=5,
         legend=False, ax=axes[1])
gdf[mgwr_filtered_t1[:, 1] == 0].plot(color='white', linewidth=0.05, edgecolor='black', ax=axes[1])
axes[1].set_title(f'(b) MGWR: NTL (BW: {mgwr_bw}), significant coeffs', fontsize=12)
axes[1].axis("off")

gdf.plot(column='mgwr_slope1', cmap='coolwarm', linewidth=0.05, scheme='FisherJenks', k=5,
         legend=False, ax=axes[2])
gdf[mgwr_filtered_tc1[:, 1] == 0].plot(color='white', linewidth=0.05, edgecolor='black', ax=axes[2])
axes[2].set_title(f'(c) MGWR: NTL (BW: {mgwr_bw}), corrected p-values', fontsize=12)
axes[2].axis("off")

plt.tight_layout()
plt.show()
```
