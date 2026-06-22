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

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/quarcs-lab/bolivia112/blob/main/notebooks/esda_inequality.ipynb)

# Spatial Inequality

An interactive tutorial measuring regional inequality across Bolivia's 112 provinces. This notebook covers the Theil index (with between/within decomposition by department), the Gini coefficient, and the Spatial Gini index to assess how much inequality is spatially structured.

> Province values are population-weighted aggregations of the underlying municipal data (intensive variables use population-weighted means, extensive variables are summed). See [`../province_aggregation_report.md`](../province_aggregation_report.md) for the aggregation methodology.

## Setup

```{code-cell} ipython3
# Install packages not included in Google Colab's default environment.
# When running locally with UV, these are already installed and this cell is harmless.
!pip install contextily libpysal inequality -q
```

```{code-cell} ipython3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import geopandas as gpd
import contextily as cx

from libpysal import weights
import inequality
from inequality.gini import Gini_Spatial

import warnings
warnings.filterwarnings('ignore')
```

## Import data

```{code-cell} ipython3
# Province boundaries (geometry + prov_id, prov, dep, dep_id)
mapURL = 'maps/bolivia112provincesOpt.geojson'
# Province-level indicators (population-weighted aggregation of the municipal data)
dataURL = 'bolivia112/bolivia112_v20260622.csv'

provMap = gpd.read_file(mapURL)
provData = pd.read_csv(dataURL)

# Merge the indicators onto the geometry using the province key prov_id
gdf = provMap.merge(provData, on='prov_id', how='left', suffixes=('', '_data'))
gdf.head(3)
```

```{code-cell} ipython3
dataDefinitions = pd.read_csv('bolivia112/definitions_bolivia112_v20260622.csv')
data_dict = dict(zip(dataDefinitions['varname'], dataDefinitions['varlabel']))
```

## Define key parameters

```{code-cell} ipython3
INDICATOR1 = 'imds'                # Sustainable Development Index (province aggregate)
INDICATOR3 = 'ln_t400NTLpc2017'    # Log nighttime lights per capita (2017)
INDICATOR4 = 'rank_imds'           # IMDS ranking

ADM1 = 'dep'                       # Department (9 departments)
ADM2 = 'prov'                      # Province (112 provinces)
```

## Distribution of indicators

```{code-cell} ipython3
sns.histplot(x=gdf[INDICATOR1], kde=True);
```

```{code-cell} ipython3
sns.histplot(x=gdf[INDICATOR3], kde=True);
```

## Theil index

```{code-cell} ipython3
theil_INDICATOR1 = inequality.theil.Theil(gdf[INDICATOR1].values).T
theil_INDICATOR1
```

```{code-cell} ipython3
theil_INDICATOR3 = inequality.theil.Theil(gdf[INDICATOR3].values).T
theil_INDICATOR3
```

### Theil decomposition

- How much inequality is *between* departments vs *within* departments?

```{code-cell} ipython3
gdf.explore(
    column=ADM1,
    tooltip=[ADM1, ADM2, INDICATOR1, INDICATOR4],
    categorical=True,
    legend=True,
    tiles='CartoDB positron',
    style_kwds=dict(color="gray", weight=0.6),
    legend_kwds=dict(colorbar=False)
)
```

```{code-cell} ipython3
theil_BW_INDICATOR1 = inequality.theil.TheilD(gdf[INDICATOR1].values, gdf[ADM1])
theil_B_INDICATOR1 = theil_BW_INDICATOR1.bg
theil_W_INDICATOR1 = theil_BW_INDICATOR1.wg
```

```{code-cell} ipython3
print("IMDS — Between-department share:", theil_B_INDICATOR1 / theil_INDICATOR1)
print("IMDS — Within-department share: ", theil_W_INDICATOR1 / theil_INDICATOR1)
```

```{code-cell} ipython3
theil_BW_INDICATOR3 = inequality.theil.TheilD(gdf[INDICATOR3].values, gdf[ADM1])
theil_B_INDICATOR3 = theil_BW_INDICATOR3.bg
theil_W_INDICATOR3 = theil_BW_INDICATOR3.wg
```

```{code-cell} ipython3
print("NTL — Between-department share:", theil_B_INDICATOR3 / theil_INDICATOR3)
print("NTL — Within-department share: ", theil_W_INDICATOR3 / theil_INDICATOR3)
```

## Gini index

```{code-cell} ipython3
print("Gini (IMDS):", inequality.gini.Gini(gdf[INDICATOR1].values).g)
print("Gini (NTL): ", inequality.gini.Gini(gdf[INDICATOR3].values).g)
```

### Spatial Gini

- What share of inequality is between neighbouring provinces?

```{code-cell} ipython3
W = weights.KNN.from_dataframe(gdf, k=6)
W.transform = 'r'
```

```{code-cell} ipython3
sg1 = Gini_Spatial(gdf[INDICATOR1], W)
print("IMDS — Spatial Gini share:", sg1.wcg_share, ", p-value:", sg1.p_sim)
```

```{code-cell} ipython3
sg3 = Gini_Spatial(gdf[INDICATOR3], W)
print("NTL — Spatial Gini share:", sg3.wcg_share, ", p-value:", sg3.p_sim)
```
