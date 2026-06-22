# GDP Data

## Overview

This directory contains Gross Domestic Product (GDP) per capita data at the province level for Bolivia, covering the 112 provinces.

> **Note:** Province values are population-weighted aggregations of the municipal data (intensive variables such as GDP per capita use a population-weighted mean; extensive variables are summed). See the [province aggregation report](../province_aggregation_report.md) for details.

## Current Status

This directory provides a long-run panel of GDP per capita estimates:

- **[gdp_perCapita_1990_2024.csv](gdp_perCapita_1990_2024.csv)** - Annual GDP per capita for the 112 provinces, 1990-2024.

Additional GDP-related information can be found in:

- **[Interactive Dashboard](https://carlos-mendez.projects.earthengine.app/view/geoexplorer1v100bolivia)** - Visualizes GDP estimates along with other indicators
- **Archive data**: [archive20250523/](../archive20250523/) - May contain historical GDP datasets

## Content

The current GDP dataset includes:

- Province GDP per capita estimates (annual, 1990-2024)
- A consistent 35-year time series of economic output per person
- Province metadata (name, department) for joining and labeling

Future extensions may include:

- Total (not per capita) province GDP
- Sectoral GDP breakdowns (agriculture, industry, services)
- GDP growth rates and trends

## Related Economic Indicators

The repository contains related economic proxies that complement the GDP data:

- **[Night-time Lights (NTL)](../ntl/)** - Proxy for economic activity and electrification
- **[SDG 8 Index](../sdg/)** - Decent Work and Economic Growth indicators
- **[Population](../pop/)** - Denominator for per capita calculations

## Variable Structure

The `gdp_perCapita_1990_2024.csv` file contains the following variables (112 rows, one per province):

| Variable Name | Description |
| --- | --- |
| **prov_id** | Unique province identifier (3-digit INE code, e.g. 405 = Litoral) for joining datasets |
| **prov** | Province name |
| **dep** | Department name |
| **dep_id** | Department identifier |
| **gdppc1990 ... gdppc2024** | GDP per capita for each year from 1990 to 2024 |

## Methodology

GDP estimates at the province level are derived by aggregating municipal estimates using population weights. The underlying municipal estimates are typically built from:

- **Satellite-based proxies**: Night-time lights, building density, land use
- **Machine learning models**: Using satellite embeddings to predict economic output
- **Statistical downscaling**: Disaggregating department-level GDP to municipalities
- **Survey-based estimates**: Household income and expenditure surveys

Per capita values are then combined into provinces as a population-weighted mean of the constituent municipalities.

## Join Key

Use `prov_id` to join GDP data with other datasets in this repository.

```python
import pandas as pd

# Load GDP per capita panel
df_gdp = pd.read_csv("gdp/gdp_perCapita_1990_2024.csv")

# Verify the row count matches the 112 provinces
assert len(df_gdp) == 112

# Merge with SDG indices on prov_id
df_sdg = pd.read_csv("sdg/sdg.csv")
df_merged = pd.merge(df_sdg, df_gdp, on="prov_id", how="inner")

# Inspect GDP per capita for 2024
print(df_merged[["prov_id", "prov", "gdppc2024"]].head())
```

## References

For GDP estimation methodologies using satellite data, see:

- [Henderson, J. V., Storeygard, A., & Weil, D. N. (2012). Measuring economic growth from outer space](https://www.aeaweb.org/articles?id=10.1257/aer.102.2.994)
- Main project README: [Data Integration Examples](../README.md)
