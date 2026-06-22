---
jupytext:
  formats: ipynb,md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.19.1
kernelspec:
  display_name: Python 3
  name: python3
---

+++ {"cell_id": "ce8e4aaee08f459f9db2136f41fe3ff7", "deepnote_app_coordinates": {"h": 24, "w": 12, "x": 0, "y": 234}, "deepnote_cell_type": "markdown", "id": "MTgK8ssKIv32"}

![](https://github.com/quarcs-lab/project2021o-notebook/blob/main/figs/cover.png?raw=true)

+++ {"cell_id": "752cd2fc884c4633a1c809546625c333", "deepnote_app_coordinates": {"h": 5, "w": 12, "x": 0, "y": null}, "deepnote_cell_type": "text-cell-h1", "formattedRanges": [], "id": "tPbPpRITIv3z", "is_collapsed": false}

```
https://shorturl.at/evEFS
```
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/quarcs-lab/bolivia112/blob/main/notebooks/eda_esda.ipynb)

# **A geocomputational notebook to monitor regional development in Bolivia**

Carlos Mendez (Nagoya Univerisity), Erick Gonzales (United Nations), Lykke Andersen (SDSN Bolivia)

This notebook analyzes regional development across Bolivia's 112 provinces. Province values are population-weighted aggregations of the underlying municipal data (intensive variables = weighted mean, extensive variables = sum); see [../province_aggregation_report.md](../province_aggregation_report.md) for the aggregation methodology.


[![DOI](https://zenodo.org/badge/683583423.svg)](https://zenodo.org/badge/latestdoi/683583423)
```
Suggested citation:
Mendez, C., Gonzales, E., & Andersen, L. (2023). A geocomputational notebook to monitor regional development in Bolivia. Zenodo. https://doi.org/10.5281/zenodo.828685
```
Github repository: https://github.com/quarcs-lab/project2021o-notebook

+++ {"cell_id": "d1fdbacb61374efdaad452451a748a64", "deepnote_cell_type": "text-cell-h2", "formattedRanges": [], "id": "op7BfWwqIv32", "is_collapsed": false}

## 1) Setup

```{code-cell}
:id: T4mxke3PJL03

# Install packages not included in Google Colab's default environment.
# When running locally with UV, these are already installed and this cell is harmless.
!pip install geopandas contextily libpysal esda splot mapclassify inequality mgwr -q
```

```{code-cell}
:id: hr0ihHLoTfR4

# Importing necessary libraries for data analysis and visualization
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import plotly.express as px
import plotly.graph_objects as go

# Importing libraries for spatial data and visualization
import geopandas as gpd
import contextily as cx

import libpysal
from libpysal  import weights
from libpysal.weights import Queen

# Exploratory Spatial Data Analysis (ESDA) tools
import mapclassify as mc
import esda
from esda.moran import Moran, Moran_Local

# Spatial plotting tools
import splot
from splot.esda import moran_scatterplot, plot_moran, lisa_cluster, plot_local_autocorrelation
from splot.libpysal import plot_spatial_weights
from splot.mapping import vba_choropleth

# Library for inequality analysis
import inequality
from inequality.gini import Gini_Spatial

# Statistical modeling
import statsmodels.api as sm
import statsmodels.formula.api as smf

# Geographically Weighted Regression (GWR) and related utilities
from mgwr.gwr import GWR, MGWR
from mgwr.sel_bw import Sel_BW
from mgwr.utils import shift_colormap, truncate_colormap

# Suppressing warnings for cleaner output
import warnings
warnings.filterwarnings('ignore')
```

+++ {"id": "qHHgLyWOL0GG"}

## 2) Import data

```{code-cell}
---
cell_id: bb7d32248f4c40079e3dd52a75e8bfe9
deepnote_app_coordinates:
  h: 5
  w: 12
  x: 0
  y: 24
deepnote_app_is_code_hidden: true
deepnote_cell_type: code
deepnote_to_be_reexecuted: false
execution_millis: 361
execution_start: 1667529252998
id: sseQMjQJIv34
is_code_hidden: false
source_hash: 50df4634
---
# Province boundaries (112 provinces) provide the geometry plus the
# COORD_X/COORD_Y centroids used later for GWR/MGWR.
# Prefer the local repository path; the raw-GitHub URL is provided as a fallback.
mapURL = 'https://raw.githubusercontent.com/quarcs-lab/bolivia112/main/maps/bolivia112provincesOpt.geojson'
# Local path (uncomment when running from the repository root):
# mapURL = 'maps/bolivia112provincesOpt.geojson'

# Province-level attribute table (all indicators keyed by prov_id). Province
# values are population-weighted aggregations of the municipal data (intensive
# vars = weighted mean, extensive vars = sum); see
# ../province_aggregation_report.md for the full methodology.
dataURL = 'https://raw.githubusercontent.com/quarcs-lab/bolivia112/main/bolivia112_v20260622.csv'
# Local path (uncomment when running from the repository root):
# dataURL = 'bolivia112_v20260622.csv'

# Read the province boundaries with GeoPandas and the attributes with pandas.
gdf_map = gpd.read_file(mapURL)
df_data = pd.read_csv(dataURL)

# Drop admin columns that also live in the attribute table to avoid merge
# collisions; keep geometry and the COORD_X/COORD_Y centroids from the map.
gdf_map = gdf_map.drop(columns=['prov', 'dep', 'dep_id', 'shapeName'])

# Merge boundaries and attributes on the province join key prov_id
gdf = gdf_map.merge(df_data, on='prov_id', how='inner')
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 277
id: UPRV-lqJUmPz
outputId: 8e460145-b4e2-4d7d-a4f5-621f3333abae
---
gdf.head(3)
```

```{code-cell}
---
cell_id: 66dc1e05e2394672ab0f1011af92fa9c
colab:
  base_uri: https://localhost:8080/
  height: 424
deepnote_app_coordinates:
  h: 28
  w: 12
  x: 0
  y: 196
deepnote_app_is_code_hidden: true
deepnote_cell_type: code
deepnote_table_loading: false
deepnote_table_state:
  filters: []
  pageIndex: 0
  pageSize: 25
  sortBy: []
deepnote_to_be_reexecuted: false
execution_millis: 111
execution_start: 1667529253366
id: LMgM9N8MIv35
is_code_hidden: false
outputId: a4ec3b6e-62fe-4752-ead4-3ef784b4bad5
source_hash: 819d7ded
---
dataDefinitions = pd.read_csv('https://raw.githubusercontent.com/quarcs-lab/project2021o-notebook/main/dataDefinitions.csv')
dataDefinitions
```

```{code-cell}
:id: EZSg8FVM1J4A

data_dict = dict(zip(dataDefinitions['Variable'], dataDefinitions['Label']))
```

+++ {"cell_id": "4d4826e2d633481bb417bcdf8f012c7d", "deepnote_app_coordinates": {"h": 3, "w": 12, "x": 0, "y": 192}, "deepnote_cell_type": "text-cell-h2", "formattedRanges": [], "id": "JgE-EaLeIv34", "is_collapsed": false}

## 3) Define key parameters

```{code-cell}
---
cell_id: 01f37b9657a14552af4519489f69caa9
deepnote_app_coordinates:
  h: 4
  w: 8
  x: 0
  y: 0
deepnote_cell_type: input-select
deepnote_to_be_reexecuted: false
deepnote_variable_custom_options: [Option 1, Option 2, sdg10_2_ge, imds]
deepnote_variable_name: INDICATOR1
deepnote_variable_options: [prov_id, prov, dep, dep_id, dep_prov,
  imds, rank_imds, population_2020, urbano_2012, sdg1_1_eepr, sdg1_1_ubn, sdg1_2_mpi,
  sdg1_4_abs, sdg2_2_cmc, sdg2_2_oww, sdg2_4_pual, sdg2_4_td, sdg3_1_idca, sdg3_2_imr,
  sdg3_2_mrc, sdg3_3_cdir, sdg3_3_di, sdg3_3_imr, sdg3_3_ti, sdg3_3_hivi, sdg3_7_afr,
  sdg4_1_ssdrm, sdg4_1_ssdrf, sdg4_4_phe, sdg4_6_lr, sdg4_c_qti, sdg4_c_qts, sdg5_1_gpsd,
  sdg5_1_gpyp, sdg5_1_gpmpi, sdg5_5_gpop, sdg6_1_dwc, sdg6_2_sc, sdg6_3_wwt, sdg7_1_ec,
  sdg7_1_rec, sdg7_1_cce, sdg7_3_co2epc, sdg8_4_rem, sdg8_5_oprm, sdg8_5_ofrm, sdg8_6_mlm,
  sdg8_6_wlm, sdg8_10_dbb, sdg8_11_idi, sdg9_1_routes, sdg9_5_cd, sdg9_5_eutf, sdg9_c_mnc,
  sdg9_c_drb, sdg10_2_gcye, sdg10_2_iec, sdg10_2_nssp, sdg11_1_hocr, sdg11_1_hno,
  sdg11_2_samt, sdg13_1_ccvi, sdg13_2_tco2e, sdg13_2_dra, sdg15_1_pa, sdg15_5_blr,
  sdg16_1_rhr, sdg16_6_pbec, sdg16_9_cr, sdg17_1_pmtax, sdg17_5_pipc, index_sdg1,
  index_sdg2, index_sdg3, index_sdg4, index_sdg5, index_sdg6, index_sdg7, index_sdg8,
  index_sdg9, index_sdg10, index_sdg11, index_sdg13, index_sdg15, index_sdg16, index_sdg17,
  pop2001, pop2002, pop2003, pop2004, pop2005, pop2006, pop2007, pop2008, pop2009,
  pop2010, pop2011, pop2012, pop2013, pop2014, pop2015, pop2016, pop2017, pop2018,
  pop2019, pop2020, ln_NTLpc2012, ln_NTLpc2013, ln_NTLpc2014, ln_NTLpc2015, ln_NTLpc2016,
  ln_NTLpc2017, ln_NTLpc2018, ln_NTLpc2019, ln_NTLpc2020, ln_t400NTLpc2012, ln_t400NTLpc2013,
  ln_t400NTLpc2014, ln_t400NTLpc2015, ln_t400NTLpc2016, ln_t400NTLpc2017, ln_t400NTLpc2018,
  ln_t400NTLpc2019, ln_t400NTLpc2020, co2015, co2016, co2017, co2018, co2019, co2020,
  tr400_co2015, tr400_co2016, tr400_co2017, tr400_co2018, tr400_co2019, tr400_co2020]
deepnote_variable_select_type: from-variable
deepnote_variable_selected_variable: variables
deepnote_variable_value: imds
execution_millis: 14
execution_start: 1667529253487
id: JWcURAH_Iv36
owner_user_id: 3e428fbe-be88-4851-af0f-3aa6c027cd24
source_hash: ae5c3e6d
---
INDICATOR1 = 'imds'
```

```{code-cell}
---
cell_id: 6f08602f403e4dfeb1de6d27d18851ca
deepnote_app_coordinates:
  h: 4
  w: 8
  x: 0
  y: 0
deepnote_cell_type: input-select
deepnote_to_be_reexecuted: false
deepnote_variable_custom_options: [Option 1, Option 2]
deepnote_variable_name: INDICATOR2
deepnote_variable_options: [prov_id, prov, dep, dep_id, dep_prov,
  imds, rank_imds, population_2020, urbano_2012, sdg1_1_eepr, sdg1_1_ubn, sdg1_2_mpi,
  sdg1_4_abs, sdg2_2_cmc, sdg2_2_oww, sdg2_4_pual, sdg2_4_td, sdg3_1_idca, sdg3_2_imr,
  sdg3_2_mrc, sdg3_3_cdir, sdg3_3_di, sdg3_3_imr, sdg3_3_ti, sdg3_3_hivi, sdg3_7_afr,
  sdg4_1_ssdrm, sdg4_1_ssdrf, sdg4_4_phe, sdg4_6_lr, sdg4_c_qti, sdg4_c_qts, sdg5_1_gpsd,
  sdg5_1_gpyp, sdg5_1_gpmpi, sdg5_5_gpop, sdg6_1_dwc, sdg6_2_sc, sdg6_3_wwt, sdg7_1_ec,
  sdg7_1_rec, sdg7_1_cce, sdg7_3_co2epc, sdg8_4_rem, sdg8_5_oprm, sdg8_5_ofrm, sdg8_6_mlm,
  sdg8_6_wlm, sdg8_10_dbb, sdg8_11_idi, sdg9_1_routes, sdg9_5_cd, sdg9_5_eutf, sdg9_c_mnc,
  sdg9_c_drb, sdg10_2_gcye, sdg10_2_iec, sdg10_2_nssp, sdg11_1_hocr, sdg11_1_hno,
  sdg11_2_samt, sdg13_1_ccvi, sdg13_2_tco2e, sdg13_2_dra, sdg15_1_pa, sdg15_5_blr,
  sdg16_1_rhr, sdg16_6_pbec, sdg16_9_cr, sdg17_1_pmtax, sdg17_5_pipc, index_sdg1,
  index_sdg2, index_sdg3, index_sdg4, index_sdg5, index_sdg6, index_sdg7, index_sdg8,
  index_sdg9, index_sdg10, index_sdg11, index_sdg13, index_sdg15, index_sdg16, index_sdg17,
  pop2001, pop2002, pop2003, pop2004, pop2005, pop2006, pop2007, pop2008, pop2009,
  pop2010, pop2011, pop2012, pop2013, pop2014, pop2015, pop2016, pop2017, pop2018,
  pop2019, pop2020, ln_NTLpc2012, ln_NTLpc2013, ln_NTLpc2014, ln_NTLpc2015, ln_NTLpc2016,
  ln_NTLpc2017, ln_NTLpc2018, ln_NTLpc2019, ln_NTLpc2020, ln_t400NTLpc2012, ln_t400NTLpc2013,
  ln_t400NTLpc2014, ln_t400NTLpc2015, ln_t400NTLpc2016, ln_t400NTLpc2017, ln_t400NTLpc2018,
  ln_t400NTLpc2019, ln_t400NTLpc2020, co2015, co2016, co2017, co2018, co2019, co2020,
  tr400_co2015, tr400_co2016, tr400_co2017, tr400_co2018, tr400_co2019, tr400_co2020]
deepnote_variable_select_type: from-variable
deepnote_variable_selected_variable: variables
deepnote_variable_value: pop2017
execution_millis: 1
execution_start: 1667529253501
id: Y_Z6lnBBIv36
source_hash: 82e60105
---
INDICATOR2 = 'pop2017'
```

```{code-cell}
---
cell_id: 30a335eb3efd4e9b85f43c6f7c900cdf
deepnote_app_coordinates:
  h: 4
  w: 8
  x: 0
  y: 0
deepnote_cell_type: input-select
deepnote_to_be_reexecuted: false
deepnote_variable_custom_options: [Option 1, Option 2]
deepnote_variable_name: INDICATOR3
deepnote_variable_options: [prov_id, prov, dep, dep_id, dep_prov,
  imds, rank_imds, population_2020, urbano_2012, sdg1_1_eepr, sdg1_1_ubn, sdg1_2_mpi,
  sdg1_4_abs, sdg2_2_cmc, sdg2_2_oww, sdg2_4_pual, sdg2_4_td, sdg3_1_idca, sdg3_2_imr,
  sdg3_2_mrc, sdg3_3_cdir, sdg3_3_di, sdg3_3_imr, sdg3_3_ti, sdg3_3_hivi, sdg3_7_afr,
  sdg4_1_ssdrm, sdg4_1_ssdrf, sdg4_4_phe, sdg4_6_lr, sdg4_c_qti, sdg4_c_qts, sdg5_1_gpsd,
  sdg5_1_gpyp, sdg5_1_gpmpi, sdg5_5_gpop, sdg6_1_dwc, sdg6_2_sc, sdg6_3_wwt, sdg7_1_ec,
  sdg7_1_rec, sdg7_1_cce, sdg7_3_co2epc, sdg8_4_rem, sdg8_5_oprm, sdg8_5_ofrm, sdg8_6_mlm,
  sdg8_6_wlm, sdg8_10_dbb, sdg8_11_idi, sdg9_1_routes, sdg9_5_cd, sdg9_5_eutf, sdg9_c_mnc,
  sdg9_c_drb, sdg10_2_gcye, sdg10_2_iec, sdg10_2_nssp, sdg11_1_hocr, sdg11_1_hno,
  sdg11_2_samt, sdg13_1_ccvi, sdg13_2_tco2e, sdg13_2_dra, sdg15_1_pa, sdg15_5_blr,
  sdg16_1_rhr, sdg16_6_pbec, sdg16_9_cr, sdg17_1_pmtax, sdg17_5_pipc, index_sdg1,
  index_sdg2, index_sdg3, index_sdg4, index_sdg5, index_sdg6, index_sdg7, index_sdg8,
  index_sdg9, index_sdg10, index_sdg11, index_sdg13, index_sdg15, index_sdg16, index_sdg17,
  pop2001, pop2002, pop2003, pop2004, pop2005, pop2006, pop2007, pop2008, pop2009,
  pop2010, pop2011, pop2012, pop2013, pop2014, pop2015, pop2016, pop2017, pop2018,
  pop2019, pop2020, ln_NTLpc2012, ln_NTLpc2013, ln_NTLpc2014, ln_NTLpc2015, ln_NTLpc2016,
  ln_NTLpc2017, ln_NTLpc2018, ln_NTLpc2019, ln_NTLpc2020, ln_t400NTLpc2012, ln_t400NTLpc2013,
  ln_t400NTLpc2014, ln_t400NTLpc2015, ln_t400NTLpc2016, ln_t400NTLpc2017, ln_t400NTLpc2018,
  ln_t400NTLpc2019, ln_t400NTLpc2020, co2015, co2016, co2017, co2018, co2019, co2020,
  tr400_co2015, tr400_co2016, tr400_co2017, tr400_co2018, tr400_co2019, tr400_co2020]
deepnote_variable_select_type: from-variable
deepnote_variable_selected_variable: variables
deepnote_variable_value: ln_t400NTLpc2017
execution_millis: 0
execution_start: 1667529253502
id: m-1Sh5dtIv36
source_hash: 2f304ee2
---
INDICATOR3 = 'ln_t400NTLpc2017'
```

```{code-cell}
---
cell_id: 034e744fd0264570b6c7064c6ab8a86e
deepnote_app_coordinates:
  h: 4
  w: 8
  x: 0
  y: 0
deepnote_cell_type: input-select
deepnote_to_be_reexecuted: false
deepnote_variable_custom_options: [Option 1, Option 2]
deepnote_variable_name: INDICATOR4
deepnote_variable_options: [prov_id, prov, dep, dep_id, dep_prov,
  imds, rank_imds, population_2020, urbano_2012, sdg1_1_eepr, sdg1_1_ubn, sdg1_2_mpi,
  sdg1_4_abs, sdg2_2_cmc, sdg2_2_oww, sdg2_4_pual, sdg2_4_td, sdg3_1_idca, sdg3_2_imr,
  sdg3_2_mrc, sdg3_3_cdir, sdg3_3_di, sdg3_3_imr, sdg3_3_ti, sdg3_3_hivi, sdg3_7_afr,
  sdg4_1_ssdrm, sdg4_1_ssdrf, sdg4_4_phe, sdg4_6_lr, sdg4_c_qti, sdg4_c_qts, sdg5_1_gpsd,
  sdg5_1_gpyp, sdg5_1_gpmpi, sdg5_5_gpop, sdg6_1_dwc, sdg6_2_sc, sdg6_3_wwt, sdg7_1_ec,
  sdg7_1_rec, sdg7_1_cce, sdg7_3_co2epc, sdg8_4_rem, sdg8_5_oprm, sdg8_5_ofrm, sdg8_6_mlm,
  sdg8_6_wlm, sdg8_10_dbb, sdg8_11_idi, sdg9_1_routes, sdg9_5_cd, sdg9_5_eutf, sdg9_c_mnc,
  sdg9_c_drb, sdg10_2_gcye, sdg10_2_iec, sdg10_2_nssp, sdg11_1_hocr, sdg11_1_hno,
  sdg11_2_samt, sdg13_1_ccvi, sdg13_2_tco2e, sdg13_2_dra, sdg15_1_pa, sdg15_5_blr,
  sdg16_1_rhr, sdg16_6_pbec, sdg16_9_cr, sdg17_1_pmtax, sdg17_5_pipc, index_sdg1,
  index_sdg2, index_sdg3, index_sdg4, index_sdg5, index_sdg6, index_sdg7, index_sdg8,
  index_sdg9, index_sdg10, index_sdg11, index_sdg13, index_sdg15, index_sdg16, index_sdg17,
  pop2001, pop2002, pop2003, pop2004, pop2005, pop2006, pop2007, pop2008, pop2009,
  pop2010, pop2011, pop2012, pop2013, pop2014, pop2015, pop2016, pop2017, pop2018,
  pop2019, pop2020, ln_NTLpc2012, ln_NTLpc2013, ln_NTLpc2014, ln_NTLpc2015, ln_NTLpc2016,
  ln_NTLpc2017, ln_NTLpc2018, ln_NTLpc2019, ln_NTLpc2020, ln_t400NTLpc2012, ln_t400NTLpc2013,
  ln_t400NTLpc2014, ln_t400NTLpc2015, ln_t400NTLpc2016, ln_t400NTLpc2017, ln_t400NTLpc2018,
  ln_t400NTLpc2019, ln_t400NTLpc2020, co2015, co2016, co2017, co2018, co2019, co2020,
  tr400_co2015, tr400_co2016, tr400_co2017, tr400_co2018, tr400_co2019, tr400_co2020]
deepnote_variable_select_type: from-variable
deepnote_variable_selected_variable: variables
deepnote_variable_value: co2017
execution_millis: 0
execution_start: 1667529253503
id: OtsxnR7AIv37
source_hash: 8e0a9f65
---
INDICATOR4 = 'rank_imds'
```

```{code-cell}
:id: GW0WF72fTgLt

INDICATOR5 = 'co2017'
```

```{code-cell}
:id: iPDRnxkvTF-s

ADM1 = 'dep'                       # Department (9 departments)
```

```{code-cell}
:id: EZbnhtMPTFf2

ADM2 = 'prov'                      # Province (112 provinces)
```

```{code-cell}
:id: gFXAEtgTTFSo

# Unit of analysis: the province (112 provinces). The municipal-level ADM3
# of the source notebook is replaced by the province here.
ADM3 = 'prov'
```

+++ {"id": "PcWpZ8VINZRu"}

## 4) Exploratory data analysis (EDA)

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 1000
id: XnDc2E3nS7en
outputId: 44aabc59-ead7-4cca-9e08-11985e0318d0
---
# Exploring data using the explore() function on the GeoDataFrame
gdf.explore(
    column=ADM1,                        # Column to visualize
    tooltip=[ADM1, ADM3, INDICATOR1, INDICATOR4],  # Information in tooltip
    categorical=True,                    # Categorical column
    legend=True,                         # Show legend
    tiles='CartoDB positron',            # Basemap style (Other options: CartoDB positron, OpenStreetMap, Stamen Terrain)
    style_kwds=dict(color="gray", weight=0.6),  # Styling for non-highlighted areas
    legend_kwds=dict(colorbar=False)     # Customize legend
)
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 424
id: l1byH1g-VDCO
outputId: 636f512c-9f83-45f5-9b22-912b72c36b7c
---
gdf[[ADM3, ADM1, INDICATOR1, INDICATOR2, INDICATOR3, INDICATOR4]].sort_values(by=INDICATOR1, ascending=False).reset_index(drop=True)
```

+++ {"cell_id": "436762013f774808ad960d72f5ca6a4d", "deepnote_app_coordinates": {"h": 3, "w": 12, "x": 0, "y": 230}, "deepnote_cell_type": "text-cell-h2", "formattedRanges": [], "id": "OoI5bX2NIv37", "is_collapsed": false}

### 4.1) Descriptive statistics

+++ {"cell_id": "681ae357ba184d9096fecc33608eab7b", "deepnote_app_coordinates": {"h": 5, "w": 12, "x": 0, "y": 0}, "deepnote_cell_type": "markdown", "id": "yCCfLg_EIv37"}

- What do we know about the centrality and dispersion of our development indicator?

```{code-cell}
---
cell_id: da8e081c88d244dfa56282e1121c240f
colab:
  base_uri: https://localhost:8080/
  height: 300
deepnote_app_coordinates:
  h: 5
  w: 12
  x: 0
  y: 30
deepnote_cell_type: code
deepnote_table_loading: false
deepnote_table_state:
  filters: []
  pageIndex: 0
  pageSize: 10
  sortBy:
  - id: imds
    type: desc
deepnote_to_be_reexecuted: false
execution_millis: 22
execution_start: 1667529253510
id: davYPzluIv37
is_code_hidden: false
outputId: 79c8346c-df6c-4546-881d-a9ccfea90866
source_hash: 118d1ff5
---
gdf[[INDICATOR1, INDICATOR2, INDICATOR3, INDICATOR4]].describe().round(2)
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 394
id: Yr2yODAitPUa
outputId: e74e5bc1-1d12-4df5-a05b-2123f9af6698
---
gdf[[ADM1, INDICATOR1]].groupby('dep').describe().round(2)
```

+++ {"cell_id": "f13548b3db814695ba3e78d625079ee2", "deepnote_app_coordinates": {"h": 5, "w": 12, "x": 0, "y": 54}, "deepnote_cell_type": "text-cell-h2", "formattedRanges": [], "id": "_PPHUHiCIv37", "is_collapsed": false}

### 4.2) Regional development differences

+++ {"cell_id": "589ee154247e4dc2987dfaf3e7cbdba1", "deepnote_app_coordinates": {"h": 5, "w": 12, "x": 0, "y": 0}, "deepnote_cell_type": "markdown", "id": "8juS6q-BIv37"}

- How is our development indicator disbributed across the 112 provinces and 9 departments of Bolivia?

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 542
id: kTSO1Bo6YIjs
outputId: 02ad8224-f4c7-4365-de00-d9aebf16cd00
---
# Creating a strip plot using Plotly Express
px.strip(
    gdf,
    x=INDICATOR1,                 # Data for x-axis
    y=ADM1,                      # Data for y-axis
    color=ADM1,                  # Color grouping based on 'dep'
    hover_name=ADM3,             # Province for hover tooltip
    hover_data=[ADM1, INDICATOR4],     # Additional data for hover tooltip
    labels=dict(data_dict)        # Custom labels from data_dict
)
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 542
id: RiiR51x2YvTo
outputId: 5188f157-2763-4020-b92a-99dfb1ae60ab
---
# Creating a histogram using Plotly Express
px.histogram(
    gdf,
    x=INDICATOR1,                    # Data for x-axis
    color=ADM1,                     # Color grouping based on 'dep'
    hover_name=ADM3,                # Province for hover tooltip
    marginal='rug',                  # Display rug plot on the marginal axis
    hover_data=[ADM1, INDICATOR4],        # Additional data for hover tooltip
    labels=dict(data_dict)           # Custom labels from data_dict
)
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 542
id: 7A36wjpJYdvj
outputId: b08df7c0-1a15-4a97-9904-941bf63b3ce9
---
# Creating a box plot using Plotly Express
px.box(
    gdf,
    x=INDICATOR1,                 # Data for x-axis
    y=ADM1,                      # Data for y-axis
    color=ADM1,                  # Color grouping based on 'dep'
    hover_name=ADM3,             # Province for hover tooltip
    hover_data=[ADM1, INDICATOR4],     # Additional data for hover tooltip
    labels=dict(data_dict)        # Custom labels from data_dict
)
```

+++ {"cell_id": "18480afe6d2640ef8f1dd51b1222e21d", "deepnote_app_coordinates": {"h": 5, "w": 12, "x": 0, "y": 96}, "deepnote_cell_type": "text-cell-h2", "formattedRanges": [], "id": "lB7-mMhMIv38", "is_collapsed": false}

### 4.3) Population and development

+++ {"cell_id": "27bb9c1b0a9649faade5c135cb24cc96", "deepnote_app_coordinates": {"h": 5, "w": 12, "x": 0, "y": 0}, "deepnote_cell_type": "markdown", "id": "1Oz5xuoLIv38"}

- Do the most populous regions tend to be more developed?

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 542
id: cEDK7PJxX_aY
outputId: 538bbb74-c9d8-402f-a0e9-c551bb499c82
---
px.bar(
    gdf.sort_values(by=INDICATOR2, ascending=True),
    x=ADM3,                    # Data for x-axis
    y=INDICATOR2,               # Data for y-axis
    log_y=False,                # Disable logarithmic y-axis scale
    hover_data=[INDICATOR1, INDICATOR2, INDICATOR4],  # Additional data for hover tooltip
    labels=dict(data_dict)         # Custom labels from data_dict
)
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 542
id: uwKiNfdOY5bg
outputId: f5f2717a-2740-4f27-dc60-ff8fdcecba71
---
# Creating a treemap using Plotly Express
px.treemap(
    gdf,
    color=INDICATOR1,                # Data for coloring
    values=INDICATOR2,                # Data for size of treemap blocks
    path=[ADM1, ADM3],             # Path for hierarchical display
    hover_name= ADM3,                # Province for hover tooltip
    hover_data=[INDICATOR4],        # Additional data for hover tooltip
    labels=dict(data_dict)           # Custom labels from data_dict
)
```

```{code-cell}
---
cell_id: 0ecdfecb1ae64b2a99dc19628ca8d4d5
colab:
  base_uri: https://localhost:8080/
  height: 542
deepnote_app_coordinates:
  h: 5
  w: 12
  x: 0
  y: 90
deepnote_cell_type: code
deepnote_to_be_reexecuted: false
execution_millis: 1015
execution_start: 1667529254670
id: xgY_0neZIv38
is_code_hidden: false
outputId: b064b5f5-2277-44a2-f2d4-0072c34b77c3
source_hash: beb9bee6
---
# Creating a sunburst plot using Plotly Express
px.sunburst(
    gdf,
    color=INDICATOR1,                # Data for coloring
    values=INDICATOR2,                # Data for size of sunburst segments
    path=[ADM1, ADM3],             # Path for hierarchical display
    hover_name=ADM3,                # Province for hover tooltip
    hover_data=[INDICATOR4],        # Additional data for hover tooltip
    labels=dict(data_dict)           # Custom labels from data_dict
)
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 542
id: glN7NntEYMv2
outputId: 78c41ea3-583d-4560-885c-494d87d8515a
---
px.scatter(
    gdf,
    x=INDICATOR2,                             # Data for x-axis
    log_x = True,
    y=INDICATOR1,                             # Data for y-axis
    color=ADM1,                              # Data for color coding
    symbol=ADM1,                             # Data for symbol coding
    hover_name=ADM3,                         # Province for hover tooltip
    trendline='ols',                          # Adding OLS trendline
    hover_data=[INDICATOR4],                 # Additional data for hover tooltip
    labels=dict(data_dict)                    # Custom labels from data_dict
)
```

+++ {"cell_id": "88396a06123545659ba24ea22f6e7e30", "deepnote_app_coordinates": {"h": 5, "w": 12, "x": 0, "y": 66}, "deepnote_cell_type": "text-cell-h2", "formattedRanges": [], "id": "z_WQiUi7Iv39", "is_collapsed": false}

### 4.4) Nighttime lights and development

+++ {"cell_id": "51163a48f024422282aac14556fdf3dc", "deepnote_app_coordinates": {"h": 5, "w": 12, "x": 0, "y": 0}, "deepnote_cell_type": "markdown", "id": "5jHa-XmoIv39"}

- Can nighttime lights help us predict regional development?

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 1000
id: 3CXPOu0gOoHm
outputId: 7afcc885-c1f1-4b75-9355-a98cbaf9b785
---
# Exploring data using the explore() function on the GeoDataFrame
gdf.explore(
    column=INDICATOR1,                 # Column to visualize
    tooltip=[ADM1, ADM3, INDICATOR1, INDICATOR4],  # Information to show in tooltip
    k=3,                               # Number of classes for visualization
    scheme='FisherJenks',              # Classification scheme (info: https://pysal.org/mapclassify/generated/mapclassify.FisherJenks.html#mapclassify.FisherJenks)
    cmap='BuPu',                   # Color map for visualization
    legend=True,                       # Show legend
    tiles= cx.providers.NASAGIBS.ViirsEarthAtNight2012,           # Basemap style (other options: https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.explore.html)
    style_kwds=dict(color="gray", weight=0.4, alpha=0.9),  # Styling for non-highlighted areas
    legend_kwds=dict(colorbar=False)   # Legend customization
)
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 542
id: soZuQzH7ZT8P
outputId: 15cf1b75-d1bd-45bc-b6f3-c580dece50d6
---
# Creating a scatter plot with Plotly Express
px.scatter(
    gdf,
    x=INDICATOR3,                            # Data for x-axis
    y=INDICATOR1,                            # Data for y-axis
    color=ADM1,                             # Data for color coding
    symbol=ADM1,                            # Data for symbol coding
    hover_name=ADM3,                        # Province for hover tooltip
    trendline='ols',                         # Adding OLS trendline
    trendline_scope='overall',               # Scope of the trendline (overall)
    hover_data=[INDICATOR3],                # Additional data for hover tooltip
    labels=dict(data_dict)                   # Custom labels from data_dict
)
```

+++ {"cell_id": "1c9d897637b14206a76148a2a7caf60f", "deepnote_app_coordinates": {"h": 5, "w": 12, "x": 0, "y": 0}, "deepnote_cell_type": "markdown", "id": "q158H3b1Iv39"}

How heterogeneious is the relatinship between regional development and nighttime lights?

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 542
id: IOr8wdbbZfRa
outputId: adb2a1da-13d0-48a2-90a9-61e714c0927a
---
# Creating a scatter plot with marginal box plots using Plotly Express
px.scatter(
    gdf,
    x=INDICATOR3,                             # Data for x-axis
    y=INDICATOR1,                             # Data for y-axis
    color=ADM1,                              # Data for color coding
    symbol=ADM1,                             # Data for symbol coding
    hover_name=ADM3,                         # Province for hover tooltip
    trendline='ols',                          # Adding OLS trendline
    marginal_x="box",                         # Display marginal box plot on x-axis
    marginal_y="box",                         # Display marginal box plot on y-axis
    hover_data=[INDICATOR4],                 # Additional data for hover tooltip
    labels=dict(data_dict)                    # Custom labels from data_dict
)
```

+++ {"id": "kqmQCBqPQgoB"}

## 5) Exploratory spatial data analysis (ESDA)

+++ {"cell_id": "7fdc498fca2b43468d91dfae42f38823", "deepnote_app_coordinates": {"h": 5, "w": 12, "x": 0, "y": 0}, "deepnote_cell_type": "text-cell-h2", "formattedRanges": [], "id": "3ASeA2tfIv39", "is_collapsed": false}

### 5.1) Spatial distribution

+++ {"id": "xZ1t4KpYDLWq"}

#### 5.1.1) Box-plot breaks

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 542
id: TDtX-JFIEViU
outputId: db5e3011-82f6-4ed3-e798-02541e2fbaa0
---
# Creating a box plot using Plotly Express
px.box(
    gdf,
    x=INDICATOR1,                 # Data for x-axis
    #y=ADM1,                      # Data for y-axis
    #color=ADM1,                  # Color grouping based on ADM1
    hover_name=ADM3,             # Province for hover tooltip
    hover_data=[INDICATOR4, ADM1],     # Additional data for hover tooltip
    labels=dict(data_dict)        # Custom labels from data_dict
)
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 1000
id: eJGYcIzhDKjV
outputId: 5fd68f3c-ecd8-4807-c745-47dbf1352089
---
# Exploring data using the explore() function on the GeoDataFrame
gdf.explore(
    column=INDICATOR1,                 # Column to visualize
    tooltip=[ADM1, ADM3, INDICATOR1, INDICATOR4],  # Information to show in tooltip
    scheme='BoxPlot',              # Classification scheme (info: https://pysal.org/mapclassify/generated/mapclassify.BoxPlot.html#mapclassify.BoxPlot)
    k=6,                            # Number of classes for coloring
    cmap='coolwarm',                   # Color map for visualization
    legend=True,                       # Show legend
    tiles='CartoDB positron',            # Basemap style (other options: https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.explore.html)
    style_kwds=dict(color="gray", weight=0.4),  # Styling for non-highlighted areas
    legend_kwds=dict(colorbar=False)   # Legend customization
)
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
id: _tNG1MrRJppD
outputId: d6929f83-7faf-4543-eddf-8bbde28a92e7
---
mc.BoxPlot(gdf[INDICATOR1])
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 583
id: ug71fbIiKAFr
outputId: b348ba76-000e-4b68-db80-a5a543a37736
---
import contextily as cx

# Create a figure and axis for plotting
fig, ax = plt.subplots(figsize=(9, 6))

# Plot the GeoDataFrame with specified settings
gdf.plot(
    column=INDICATOR1,              # Data for coloring
    scheme='BoxPlot',           # Classification scheme
    cmap='coolwarm',                # Color map for visualization
    edgecolor='k',                  # Color of edges
    linewidth=0.5,                  # Width of edge lines
    alpha=0.8,                      # Transparency
    legend=True,                    # Show legend
    ax=ax,                          # Specify the axis for plotting
    legend_kwds={'bbox_to_anchor': (1.00, 0.92)}  # Legend customization
)

# Adding a basemap using contextily
cx.add_basemap(
    ax,                             # Axis to add basemap to
    crs=gdf.crs.to_string(),         # Coordinate reference system
    source=cx.providers.Stamen.TonerHybrid,  # Basemap source
    attribution=False               # Disable attribution
)

# Set plot title and adjust layout
plt.title('Spatial distribution: Three natural breaks')
plt.tight_layout()

# Turn off axis display
ax.axis("off")

# Display the plot
plt.show()
```

+++ {"id": "8Im3S0aBC6yP"}

#### 5.1.2) Fisher-Jenks breaks

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 1000
id: ProSA9MXZpy5
outputId: 54d9b567-eaa4-4022-a6db-d3d438890cd7
---
# Exploring data using the explore() function on the GeoDataFrame
gdf.explore(
    column=INDICATOR1,                 # Column to visualize
    tooltip=[ADM1, ADM3, INDICATOR1, INDICATOR4],  # Information to show in tooltip
    k=3,                               # Number of classes for visualization
    scheme='FisherJenks',              # Classification scheme (info: https://pysal.org/mapclassify/generated/mapclassify.FisherJenks.html#mapclassify.FisherJenks)
    cmap='coolwarm',                   # Color map for visualization
    legend=True,                       # Show legend
    tiles='CartoDB positron',            # Basemap style (other options: https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.explore.html)
    style_kwds=dict(color="gray", weight=0.4),  # Styling for non-highlighted areas
    legend_kwds=dict(colorbar=False)   # Legend customization
)
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
id: qevIRWERJspo
outputId: f883c856-91ab-492c-a768-fedd2773f15a
---
mc.FisherJenks(gdf[INDICATOR1], k=3)
```

```{code-cell}
---
cell_id: 65d18ddb3d4f46c2a0460538198755ad
colab:
  base_uri: https://localhost:8080/
  height: 583
deepnote_app_coordinates:
  h: 5
  w: 12
  x: 0
  y: 0
deepnote_cell_type: code
deepnote_to_be_reexecuted: false
execution_millis: 2124
execution_start: 1667529255250
id: mP-LAGS9Iv39
outputId: 52210d8c-b299-44a1-ac96-afce50c82884
source_hash: 3bd74f24
---
import contextily as cx

# Create a figure and axis for plotting
fig, ax = plt.subplots(figsize=(9, 6))

# Plot the GeoDataFrame with specified settings
gdf.plot(
    column=INDICATOR1,              # Data for coloring
    scheme='FisherJenks',           # Classification scheme
    k=3,                            # Number of classes for coloring
    cmap='coolwarm',                # Color map for visualization
    edgecolor='k',                  # Color of edges
    linewidth=0.5,                  # Width of edge lines
    alpha=0.8,                      # Transparency
    legend=True,                    # Show legend
    ax=ax,                          # Specify the axis for plotting
    legend_kwds={'bbox_to_anchor': (1.00, 0.92)}  # Legend customization
)

# Adding a basemap using contextily
cx.add_basemap(
    ax,                             # Axis to add basemap to
    crs=gdf.crs.to_string(),         # Coordinate reference system
    source=cx.providers.Stamen.TonerHybrid,  # Basemap source
    attribution=False               # Disable attribution
)

# Set plot title and adjust layout
plt.title('Spatial distribution: Three natural breaks')
plt.tight_layout()

# Turn off axis display
ax.axis("off")

# Display the plot
plt.show()
```

+++ {"cell_id": "81b451cebffe4a76a04205c7c7d3af56", "deepnote_app_coordinates": {"h": 5, "w": 12, "x": 0, "y": 126}, "deepnote_cell_type": "text-cell-h2", "formattedRanges": [], "id": "ILWNZyUkIv3-", "is_collapsed": false}

### 5.2) Spatial dependence

+++ {"cell_id": "bcd469c4776a4f33afaf84c73ec63dc7", "deepnote_app_coordinates": {"h": 5, "w": 12, "x": 0, "y": 0}, "deepnote_cell_type": "markdown", "id": "RjIcSBGJIv3-"}

- To what extent is the performance of a region similar to that of its neighbours?
- To what extent is there is an overall pattern of "clustering"?
- Where can we find statistically significant spatial clusters?
- Where can we find statistically significant spatial outliers?

+++ {"id": "-R7WuY9EDUw6"}

#### 5.2.1) Spatial connectivity

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 824
id: Txiy8di4aLhR
outputId: 266b0761-552f-4c3a-fb50-6de901715e19
---
# Create K-nearest neighbors spatial weights
W = weights.KNN.from_dataframe(gdf, k=6)

# Transform the weights to row-standardized
W.transform = 'r'

# Plot the spatial weights using splot
plot_spatial_weights(W, gdf)
```

+++ {"id": "_E_xsOEkCXBk"}

#### 5.2.2) Global dependence

```{code-cell}
:id: HcdNWVaxwaZ4

# List of columns to select from the GeoDataFrame
myLIST = [ADM1, ADM3, INDICATOR1]
# Create a new DataFrame with selected columns
df_MORAN = gdf[myLIST]
# Calculate spatial lag of INDICATOR1 using the specified weights
df_MORAN["WxINDICATOR1"] = weights.lag_spatial(W, df_MORAN.iloc[: , -1])
```

```{code-cell}
---
cell_id: da1dc902980a4c7ab3424ebd8e60a1e6
colab:
  base_uri: https://localhost:8080/
  height: 542
deepnote_app_coordinates:
  h: 24
  w: 12
  x: 0
  y: 284
deepnote_app_is_code_hidden: true
deepnote_cell_type: code
deepnote_to_be_reexecuted: false
execution_millis: 802
execution_start: 1667529258604
id: X9fduQ3wIv3-
is_code_hidden: false
outputId: 9972c442-ed5e-499b-bf0f-fda239bed3c3
source_hash: ae2af11d
---
# Creating a scatter plot with Plotly Express
px.scatter(
    df_MORAN,
    x=INDICATOR1,                            # Data for x-axis
    y="WxINDICATOR1",                        # Data for y-axis
    hover_name=ADM3,                        # Province for hover tooltip
    hover_data=[ADM1, INDICATOR1, 'WxINDICATOR1'],  # Additional data for hover tooltip
    trendline="ols",                         # Adding OLS trendline
    marginal_x="box",                        # Display marginal box plot on x-axis
    marginal_y="box",                        # Display marginal box plot on y-axis
    labels=dict(data_dict)                    # Custom labels from data_dict
)
```

+++ {"id": "pP0e8udaCp-L"}

#### 5.2.3) Local dependence

```{code-cell}
---
cell_id: c68683a216af4a149740251dbd20e26f
deepnote_app_coordinates:
  h: 5
  w: 12
  x: 0
  y: 120
deepnote_cell_type: code
deepnote_to_be_reexecuted: false
execution_millis: 1995
execution_start: 1667529258685
id: Z5AjodNsIv3_
is_code_hidden: false
source_hash: 7f6be6b1
---
# Calculate global Moran's I
globalMoran = Moran(gdf[INDICATOR1], W)
MoranI = globalMoran.I
MoranI = "{:.2f}".format(MoranI)

# Calculate local indicators of spatial association
localMoran = Moran_Local(gdf[INDICATOR1], W, permutations = 999, seed=12345)
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 506
id: FYglb4nkaxoP
outputId: 4d4156f7-fd86-44f3-ec70-2cb87d77e3fc
---
# Create subplots for visualizations
fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(12, 5))

# Plotting Moran scatterplot
moran_scatterplot(localMoran, p=0.10, aspect_equal=False, zstandard=False, ax=axes[0])

# Plotting Local Indicators of Spatial Association (LISA) clusters
lisa_cluster(localMoran, gdf, p=0.10, legend_kwds={'bbox_to_anchor': (0.02, 0.90)}, ax=axes[1])

# Setting labels and titles for the plots
axes[0].set_xlabel('Indicator')
axes[0].set_ylabel('Spatial lag of indicator')
axes[0].set_title(f"(a) Moran scatterplot (Moran's I = {MoranI})")
axes[1].set_title("(b) Spatial clusters and outliers (p < 0.10)")

# Display the plots
plt.show()
```

+++ {"cell_id": "e8394c0c7e144a6b9f9272d088e2b633", "deepnote_app_coordinates": {"h": 5, "w": 12, "x": 0, "y": 0}, "deepnote_cell_type": "text-cell-h2", "formattedRanges": [], "id": "cuDT3DJPIv3_", "is_collapsed": false}

### 5.3) Spatial inequality

```{code-cell}
---
cell_id: c447e3be52484134bdb5f85d102c17cf
colab:
  base_uri: https://localhost:8080/
  height: 449
deepnote_app_coordinates:
  h: 5
  w: 12
  x: 0
  y: 0
deepnote_cell_type: code
deepnote_to_be_reexecuted: false
execution_millis: 1109
execution_start: 1667529261092
id: rm1VwT9TIv3_
outputId: a5e4e42d-376e-4f3e-bae8-eb7832c3a23f
source_hash: 8ec252f5
---
# Create a histogram plot using Seaborn
sns.histplot(x=gdf[INDICATOR1], kde=True);
```

```{code-cell}
---
cell_id: a72395fa9d72448fb2ff9cd31081c480
colab:
  base_uri: https://localhost:8080/
  height: 450
deepnote_app_coordinates:
  h: 5
  w: 12
  x: 0
  y: 0
deepnote_cell_type: code
deepnote_to_be_reexecuted: false
execution_millis: 932
execution_start: 1667529261297
id: X8FiY7XDIv3_
outputId: 40bfb71f-ad04-4874-c728-6c5c291391e5
source_hash: '26726851'
---
# Create a histogram plot using Seaborn
sns.histplot(x=gdf[INDICATOR3], kde=True);
```

+++ {"id": "vYqTpq11B_Dj"}

#### 5.3.1) Theil index

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
id: 0uhEZiu63HjV
outputId: bbc7ce80-9f65-4243-c9ec-2504c219dc20
---
theil_INDICATOR1 = inequality.theil.Theil(gdf[INDICATOR1].values).T
theil_INDICATOR1
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
id: i3ANqN_w49fp
outputId: b0517f5e-2572-467e-d7a2-958228668ef9
---
theil_INDICATOR3 = inequality.theil.Theil(gdf[INDICATOR3].values).T
theil_INDICATOR3
```

+++ {"id": "FOEjl5zt3Je4"}

Theil index decomposition

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 1000
id: hhvNFPTMWFjt
outputId: 133a645c-129c-4eea-babd-d74657b7752c
---
# Exploring data using the explore() function on the GeoDataFrame
gdf.explore(
    column=ADM1,                        # Column to visualize
    tooltip=[ADM1, ADM3, INDICATOR1, INDICATOR4],  # Information in tooltip
    categorical=True,                    # Categorical column
    legend=True,                         # Show legend
    tiles='CartoDB positron',            # Basemap style
    style_kwds=dict(color="gray", weight=0.6),  # Styling for non-highlighted areas
    legend_kwds=dict(colorbar=False)     # Customize legend

)
```

```{code-cell}
:id: bLP-wGOO3MYA

theil_BW_INDICATOR1 = inequality.theil.TheilD(gdf[INDICATOR1].values, gdf[ADM1])
```

```{code-cell}
:id: sgk7x7-aCNyQ

theil_B_INDICATOR1 = theil_BW_INDICATOR1.bg
theil_W_INDICATOR1 = theil_BW_INDICATOR1.wg
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
id: QCc7z-EyCZnL
outputId: 385c4aaf-0f1f-4726-89bd-ffacef72dcd5
---
theil_B_INDICATOR1/theil_INDICATOR1
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
id: MFtwgQjkVnK6
outputId: b77be129-4870-4c7c-d852-e704e9cafab7
---
theil_W_INDICATOR1/theil_INDICATOR1
```

```{code-cell}
:id: JV4xCTGeVyS-

theil_BW_INDICATOR3 = inequality.theil.TheilD(gdf[INDICATOR3].values, gdf[ADM1])
```

```{code-cell}
:id: 2dWtYL-8V15T

theil_B_INDICATOR3 = theil_BW_INDICATOR3.bg
theil_W_INDICATOR3 = theil_BW_INDICATOR3.wg
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
id: 6-seSgbMV1r5
outputId: dc32b793-de17-490d-c16a-5043aa087dc4
---
theil_B_INDICATOR3/theil_INDICATOR3
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
id: 2y6wYhFQV1i_
outputId: 9c9a0e06-7d0c-40f1-d969-2cf88d1cd64f
---
theil_W_INDICATOR3/theil_INDICATOR3
```

+++ {"id": "vhKR23ODCJ5G"}

#### 5.3.2) Gini index

```{code-cell}
---
cell_id: f6775501998441f98967afd069b6963a
colab:
  base_uri: https://localhost:8080/
deepnote_app_coordinates:
  h: 5
  w: 12
  x: 0
  y: 0
deepnote_cell_type: code
deepnote_to_be_reexecuted: false
execution_millis: 711
execution_start: 1667529261520
id: sjQ9a_qtIv4A
outputId: 66e5a5ae-91ad-4c77-b355-2c01c5dc0f3d
source_hash: 7c1e9574
---
inequality.gini.Gini(gdf[INDICATOR1].values).g
```

```{code-cell}
---
cell_id: 8b06891b47c04766b3c7d5123906794d
colab:
  base_uri: https://localhost:8080/
deepnote_app_coordinates:
  h: 5
  w: 12
  x: 0
  y: 0
deepnote_cell_type: code
deepnote_to_be_reexecuted: false
execution_millis: 711
execution_start: 1667529261521
id: 3wLgkJ1tIv4A
outputId: 12d2f347-1132-4617-b1fe-a81404c36c89
source_hash: c96a6679
---
inequality.gini.Gini(gdf[INDICATOR3].values).g
```

+++ {"cell_id": "a038b5694fde49179043b31a4afbf5a7", "deepnote_app_coordinates": {"h": 5, "w": 12, "x": 0, "y": 0}, "deepnote_cell_type": "markdown", "id": "sGvsI2ScIv4A"}

Let's compute the spatial gini index

```{code-cell}
---
cell_id: 2e6bc07e513748f79534bd7e328e7099
colab:
  base_uri: https://localhost:8080/
deepnote_app_coordinates:
  h: 5
  w: 12
  x: 0
  y: 0
deepnote_cell_type: code
deepnote_to_be_reexecuted: false
execution_millis: 710
execution_start: 1667529261522
id: BWAp9HQ1Iv4B
outputId: 4979a6fe-826d-4c43-a7bd-0dc3fb4187c3
source_hash: 1d9a5f5a
---
Gini_Spatial(gdf[INDICATOR1], W).wcg_share
```

```{code-cell}
---
cell_id: 92f3601b982646c2b86c8fc39cab5b00
colab:
  base_uri: https://localhost:8080/
deepnote_app_coordinates:
  h: 5
  w: 12
  x: 0
  y: 0
deepnote_cell_type: code
deepnote_to_be_reexecuted: false
execution_millis: 136
execution_start: 1667529261679
id: RHrfIvMVIv4B
outputId: b285e5eb-2e8e-4e87-ec4e-a3a915a8acae
source_hash: f1d31cc7
---
Gini_Spatial(gdf[INDICATOR1], W).p_sim
```

```{code-cell}
---
cell_id: 0a9132de7e914c15924042fc568a73ac
colab:
  base_uri: https://localhost:8080/
deepnote_app_coordinates:
  h: 5
  w: 12
  x: 0
  y: 0
deepnote_cell_type: code
deepnote_to_be_reexecuted: false
execution_millis: 418
execution_start: 1667529261816
id: hoZe9bO_Iv4B
outputId: 214904ea-405b-4c84-f8e1-cbbf91df2afc
source_hash: 96941f72
---
Gini_Spatial(gdf[INDICATOR3], W).wcg_share
```

```{code-cell}
---
cell_id: a3799e521dc3411a80fe7cedf15072ce
colab:
  base_uri: https://localhost:8080/
deepnote_app_coordinates:
  h: 5
  w: 12
  x: 0
  y: 0
deepnote_cell_type: code
deepnote_to_be_reexecuted: false
execution_millis: 318
execution_start: 1667529261962
id: 1scGEBiNIv4B
outputId: 9f77d3f8-5c0e-4e29-e5fc-e106cf38add5
source_hash: e805a86e
---
Gini_Spatial(gdf[INDICATOR3], W).p_sim
```

+++ {"cell_id": "47746d95724a4663960ef2bb2437054c", "deepnote_app_coordinates": {"h": 5, "w": 12, "x": 0, "y": 0}, "deepnote_cell_type": "text-cell-h2", "formattedRanges": [], "id": "oOCDUdF2Iv4B", "is_collapsed": false}

### 5.4) Spatial heterogeneity

```{code-cell}
---
cell_id: 09e0bd034d274fc09d1507e7be435e04
colab:
  base_uri: https://localhost:8080/
deepnote_app_coordinates:
  h: 5
  w: 12
  x: 0
  y: 0
deepnote_cell_type: code
deepnote_to_be_reexecuted: false
execution_millis: 1
execution_start: 1667529262097
id: SAHicvQ4Iv4B
outputId: f01ae975-2e2b-492f-ba6e-368e90209252
source_hash: a7ec47df
---
# Reshape the data for GWR regression
y = gdf[INDICATOR1].values.reshape((-1,1))
y.shape
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
id: CqjFNTaj-NwM
outputId: 7746c912-3804-41bc-c986-278687717fb5
---
# Reshape the data for GWR regression
X = gdf[INDICATOR3].values.reshape((-1,1))
X.shape
```

```{code-cell}
---
cell_id: 17a6b9dc932947028d56fc8790a1b918
deepnote_app_coordinates:
  h: 5
  w: 12
  x: 0
  y: 0
deepnote_cell_type: code
deepnote_to_be_reexecuted: false
execution_millis: 1
execution_start: 1667529262098
id: Fv97y1C4Iv4C
source_hash: 3f725c09
---
# Create coordinate pairs
u = gdf['COORD_X']
v = gdf['COORD_Y']
coords = list(zip(u,v))
```

+++ {"id": "fsUYjZTQ9QQk"}

#### 5.4.1) GWR analysis

```{code-cell}
---
cell_id: 8647143988ef42f392b75859bb551ef4
deepnote_app_coordinates:
  h: 5
  w: 12
  x: 0
  y: 0
deepnote_cell_type: code
deepnote_to_be_reexecuted: false
execution_millis: 9227
execution_start: 1667529262099
id: 2d6DujsMIv4C
source_hash: b56eb5ba
---
# Perform bandwidth selection for Geographically Weighted Regression (GWR)
gwr_selector = Sel_BW(coords, y, X, spherical = True)
gwr_bw = gwr_selector.search(criterion='AICc')
```

```{code-cell}
---
cell_id: d97c6428871d4fb685f09111490d2a92
colab:
  base_uri: https://localhost:8080/
deepnote_app_coordinates:
  h: 5
  w: 12
  x: 0
  y: 0
deepnote_cell_type: code
deepnote_to_be_reexecuted: false
execution_millis: 150
execution_start: 1667529271420
id: UyzEZFeaIv4C
outputId: 9fee98fe-0fdf-44e0-d4c9-2996873a6627
source_hash: 621037c3
---
# Print bandwidth interval
print('GWR bandwidth =', gwr_bw)
```

```{code-cell}
---
cell_id: 95fc86b4fa82405eaff241e32f388a1e
colab:
  base_uri: https://localhost:8080/
deepnote_app_coordinates:
  h: 5
  w: 12
  x: 0
  y: 0
deepnote_cell_type: code
deepnote_to_be_reexecuted: false
execution_millis: 602
execution_start: 1667529271423
id: wjfmukamIv4C
outputId: a08a1ec2-13c8-4801-f331-1519a4effe3c
source_hash: c37c31a3
---
# Perform Geographically Weighted Regression (GWR) and get results
gwr_results = GWR(coords, y, X, gwr_bw).fit()

# Display summary of GWR results
gwr_results.summary()
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
id: oMQ2wlQ6_Wkb
outputId: 6c459882-618f-4795-d49d-0117de4b4427
---
# Print bandwidth interval
gwr_bw_ci = gwr_results.get_bws_intervals(gwr_selector)
print(gwr_bw_ci)
```

```{code-cell}
---
cell_id: ffb9a0d3532a4b249a86d976fe14c3d5
colab:
  base_uri: https://localhost:8080/
deepnote_app_coordinates:
  h: 5
  w: 12
  x: 0
  y: 0
deepnote_cell_type: code
deepnote_to_be_reexecuted: false
execution_millis: 5
execution_start: 1667529272027
id: 7o9sThoAIv4C
outputId: 71c6146b-7040-4134-938e-16167953aa5d
source_hash: 797207d5
---
# As reference, here is the (mean) R2, AIC, and AICc
print('Mean R2 =', gwr_results.R2)
print('AIC =',     gwr_results.aic)
print('AICc =',    gwr_results.aicc)
```

```{code-cell}
---
cell_id: 4a544771f59c4658b7598f54f8b7fdd9
deepnote_app_coordinates:
  h: 5
  w: 12
  x: 0
  y: 0
deepnote_cell_type: code
deepnote_to_be_reexecuted: false
execution_millis: 35
execution_start: 1667529272033
id: u3jDIyvzIv4C
source_hash: e55f639c
---
# Add R2 to GeoDataframe
gdf['gwr_R2'] = gwr_results.localR2
```

```{code-cell}
---
cell_id: ad0d7fbdf6df447492715848d03b79c7
colab:
  base_uri: https://localhost:8080/
  height: 1000
deepnote_app_coordinates:
  h: 5
  w: 12
  x: 0
  y: 0
deepnote_cell_type: code
deepnote_to_be_reexecuted: false
execution_millis: 802
execution_start: 1667529272071
id: qrKs4h-zIv4C
outputId: a8ccfdcb-15a6-4785-fd73-16957312c718
source_hash: e7d3c632
---
# Visualizing local R-squared using the explore() function
gdf.explore(
    column='gwr_R2',                   # Column to visualize
    tooltip=[ADM1, ADM3, 'gwr_R2',   # Information to show in tooltip
             INDICATOR4, INDICATOR1, INDICATOR3],  # Additional attributes
    k=5,                               # Number of classes for visualization
    scheme='FisherJenks',              # Classification scheme
    cmap='coolwarm',                   # Color map for visualization
    legend=True,                       # Show legend
    tiles='CartoDB dark_matter',       # Basemap style
    style_kwds=dict(color="gray", weight=0.4),  # Styling for non-highlighted areas
    legend_kwds=dict(colorbar=False)   # Legend customization
)
```

```{code-cell}
---
cell_id: e4db1a1b9a364ac7b0cfa82244b1eba2
deepnote_app_coordinates:
  h: 5
  w: 12
  x: 0
  y: 0
deepnote_cell_type: code
deepnote_to_be_reexecuted: false
execution_millis: 43898147
execution_start: 1667529272495
id: 4DheZFweIv4C
source_hash: 501b46d0
---
# Add coefficients to data frame
gdf['gwr_intercept'] = gwr_results.params[:,0]
gdf['gwr_slope1']     = gwr_results.params[:,1]
```

```{code-cell}
---
cell_id: 1e056e41a7314906b5ebc748fa5979bd
deepnote_app_coordinates:
  h: 5
  w: 12
  x: 0
  y: 0
deepnote_cell_type: code
deepnote_to_be_reexecuted: false
execution_millis: 43898147
execution_start: 1667529272496
id: LIQl9-X0Iv4D
source_hash: 8110c2bb
---
# Filter t-values: standard alpha = 0.05
gwr_filtered_t1 = gwr_results.filter_tvals(alpha = 0.05)
```

```{code-cell}
---
cell_id: 34a772f12a6044b2be47312a48743c8b
deepnote_app_coordinates:
  h: 5
  w: 12
  x: 0
  y: 0
deepnote_cell_type: code
deepnote_to_be_reexecuted: false
execution_millis: 43898144
execution_start: 1667529272500
id: 6WRjI0X7Iv4D
source_hash: 4aabff8a
---
# Filter t-values: corrected alpha due to multiple testing
gwr_filtered_tc1 = gwr_results.filter_tvals()
```

```{code-cell}
---
cell_id: dcfe7d4668334cb5a435a856ccf2fe0f
colab:
  base_uri: https://localhost:8080/
  height: 1000
deepnote_app_coordinates:
  h: 5
  w: 12
  x: 0
  y: 0
deepnote_cell_type: code
deepnote_to_be_reexecuted: false
execution_millis: 1079
execution_start: 1667529272501
id: 2Sa4GgzzIv4D
outputId: 42fdd0f7-1bca-44d2-d290-fc2951220502
source_hash: e500566d
---
# Slope heterogeneity exploration using geopandas' explore() function
gdf.explore(
    column='gwr_slope1',                   # Column to visualize
    tooltip=['dep', 'prov', 'gwr_slope1',   # Information to show in tooltip
             'rank_imds', INDICATOR1, INDICATOR3],  # Additional attributes
    k=5,                                  # Number of classes for visualization
    scheme='FisherJenks',                 # Classification scheme
    cmap='coolwarm',                      # Color map for visualization
    legend=True,                          # Show legend
    tiles='CartoDB dark_matter',          # Basemap style
    style_kwds=dict(color="gray", weight=0.4),  # Styling for non-highlighted areas
    legend_kwds=dict(colorbar=False)      # Legend customization
)
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 607
id: upPbkNweXw69
outputId: 525b0a1a-b226-458d-99dc-61737c462243
---
# Create subplots for visualizations
fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(18, 6))

# Plotting the first map
gdf.plot(column='gwr_slope1', cmap='coolwarm', linewidth=0.01, scheme='FisherJenks', k=5,
         legend=True, legend_kwds={'bbox_to_anchor': (1.10, 0.96)}, ax=axes[0])
axes[0].set_title('(a) GWR: Nighttime lights (BW: ' + str(gwr_bw) + '), all coeffs', fontsize=12)
axes[0].axis("off")

# Plotting the second map
gdf.plot(column='gwr_slope1', cmap='coolwarm', linewidth=0.05, scheme='FisherJenks', k=5,
         legend=False, legend_kwds={'bbox_to_anchor': (1.10, 0.96)}, ax=axes[1])
gdf[gwr_filtered_t1[:, 1] == 0].plot(color='white', linewidth=0.05, edgecolor='black', ax=axes[1])
axes[1].set_title('(b) GWR: Nighttime lights (BW: ' + str(gwr_bw) + '), significant coeffs', fontsize=12)
axes[1].axis("off")

# Plotting the third map
gdf.plot(column='gwr_slope1', cmap='coolwarm', linewidth=0.05, scheme='FisherJenks', k=5,
         legend=False, legend_kwds={'bbox_to_anchor': (1.10, 0.96)}, ax=axes[2])
gdf[gwr_filtered_tc1[:, 1] == 0].plot(color='white', linewidth=0.05, edgecolor='black', ax=axes[2])
axes[2].set_title('(c) GWR: Nighttime lights (BW: ' + str(gwr_bw) + '), significant coeffs and corr. p-values', fontsize=12)
axes[2].axis("off")

# Adjust layout and display the plots
plt.tight_layout()
plt.show()
```

+++ {"id": "zo8PTvxW9GmX"}

#### 5.4.2) MGWR analysis

```{code-cell}
:id: d-fLhbtb9F7b

# Standardize variable for scale comparison
Zy = (y - y.mean(axis=0)) / y.std(axis=0)
ZX = (X - X.mean(axis=0)) / X.std(axis=0)
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 66
  referenced_widgets: [e7dd707bfea149b2947f48f5d2957ad2, 471fbde055ba48c18c3f3f6e18593471,
    27b7a4b6d7db42d598905ed936fffe80, 0f27ca18075648618296ac7da0ac5d0f, b68183337a7646419547cf7c60fa1337,
    3c28a63d13cc4d5aa5a556f81c3a93f1, f6bc23c05a494a6d86ce065c618d90c0, 66d2185709bd48d0a162921dda1e6864,
    bbdfa3a9e41b4b5cbc45390cd78343c8, 349f4a35bc664181a6011a6f7a9f3c5e, 2d0ca32dbcae48d7bcb076b61b6b3dc2]
id: 7oZMKqd49pyq
outputId: 4b13ea6c-a052-4170-cb29-42a7ed678f9a
---
# Perform bandwidth selection for Multiscale Geographically Weighted Regression (MGWR)
mgwr_selector = Sel_BW(coords, Zy, ZX, multi=True, spherical = True)
mgwr_bw = mgwr_selector.search(criterion='AICc')
mgwr_bw
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 987
  referenced_widgets: [d8c307f5db7b4e77a49c7cc9760e281b, cfe3e20b3be640558b2e40ba8172f042,
    6434615764dc49829d942e3cfa94a56e, caab9c0aced74f53b122418ff8dd6550, 5774bf6b4b064d288ef22488957a23ca,
    98c82a642a7142ba9273d15534331169, fb5c8e2f19f14fc0ad408b4d99a7e740, 8f398a8598ad4ab1b223da203657fae1,
    b9458796798b403f86e6df2eb636190a, 35c160c276a0491a83569c44f8dd2478, 1b0b4da0ad19473c80f5e8cdc62b468a]
id: 5S1yzK5p-72k
outputId: 35bf3921-60ce-4bfb-d06f-b253756f4477
---
# Fit MGWR model
mgwr_results = MGWR(coords, Zy, ZX, mgwr_selector).fit()
mgwr_results.summary()
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
id: 9rHFwtwc_KmW
outputId: c10371bc-fe36-4c46-f95e-da3c2bdf68d3
---
#Show bandwidth intervals
mgwr_bw_ci = mgwr_results.get_bws_intervals(mgwr_selector)
print(mgwr_bw_ci)
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
id: vE12DFTc_QOT
outputId: d4a28da9-9469-41bd-9028-d28ce43a177a
---
# As reference, here is the (mean) R2, AIC, and AICc
print('Mean R2 =', mgwr_results.R2)
print('AIC =',     mgwr_results.aic)
print('AICc =',    mgwr_results.aicc)
```

```{code-cell}
:id: 1Ek-I2is_-IZ

# Add coefficients to data frame
gdf['mgwr_intercept'] = mgwr_results.params[:,0]
gdf['mgwr_slope1']     = mgwr_results.params[:,1]
```

```{code-cell}
:id: BcDsKJDlAJGP

# Filter t-values: standard alpha = 0.05
mgwr_filtered_t1 = mgwr_results.filter_tvals(alpha = 0.05)
```

```{code-cell}
:id: AGPhTMt6APJ4

# Filter t-values: corrected alpha due to multiple testing
mgwr_filtered_tc1 = mgwr_results.filter_tvals()
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 1000
id: n_gkVbFYAZcK
outputId: 5b308cdf-fe08-468e-c181-badc8aa37d8c
---
# Slope heterogeneity exploration using geopandas' explore() function
gdf.explore(
    column='mgwr_slope1',                  # Column to visualize
    tooltip=[ADM1, ADM3, 'mgwr_slope1',  # Information to show in tooltip
             INDICATOR4, INDICATOR1, INDICATOR3],  # Additional attributes
    k=5,                                  # Number of classes for visualization
    scheme='FisherJenks',                 # Classification scheme
    cmap='coolwarm',                      # Color map for visualization
    legend=True,                          # Show legend
    tiles='CartoDB dark_matter',          # Basemap style
    style_kwds=dict(color="gray", weight=0.4),  # Styling for non-highlighted areas
    legend_kwds=dict(colorbar=False)      # Legend customization
)
```

```{code-cell}
---
colab:
  base_uri: https://localhost:8080/
  height: 607
id: 0FAP88lDAkuo
outputId: 2cd119f2-52e6-4c83-a4dd-5b62365511e8
---
# Create subplots for visualizations
fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(18, 6))

# Plotting the first map
gdf.plot(column='mgwr_slope1', cmap='coolwarm', linewidth=0.01, scheme='FisherJenks', k=5,
         legend=True, legend_kwds={'bbox_to_anchor': (1.10, 0.96)}, ax=axes[0])
axes[0].set_title('(a) MGWR: Nighttime lights (BW: ' + str(mgwr_bw) + '), all coeffs', fontsize=12)
axes[0].axis("off")

# Plotting the second map
gdf.plot(column='mgwr_slope1', cmap='coolwarm', linewidth=0.05, scheme='FisherJenks', k=5,
         legend=False, legend_kwds={'bbox_to_anchor': (1.10, 0.96)}, ax=axes[1])
gdf[mgwr_filtered_t1[:, 1] == 0].plot(color='white', linewidth=0.05, edgecolor='black', ax=axes[1])
axes[1].set_title('(b) MGWR: Nighttime lights (BW: ' + str(mgwr_bw) + '), significant coeffs', fontsize=12)
axes[1].axis("off")

# Plotting the third map
gdf.plot(column='mgwr_slope1', cmap='coolwarm', linewidth=0.05, scheme='FisherJenks', k=5,
         legend=False, legend_kwds={'bbox_to_anchor': (1.10, 0.96)}, ax=axes[2])
gdf[mgwr_filtered_tc1[:, 1] == 0].plot(color='white', linewidth=0.05, edgecolor='black', ax=axes[2])
axes[2].set_title('(c) MGWR: Nighttime lights (BW: ' + str(mgwr_bw) + '), significant coeffs and corr. p-values', fontsize=12)
axes[2].axis("off")

# Adjust layout and display the plots
plt.tight_layout()
plt.show()
```
