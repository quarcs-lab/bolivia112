# GDP Data

## Overview

This directory contains Gross Domestic Product (GDP) per capita data at the province level for Bolivia, covering the 112 provinces.

> **Note:** GDP per capita here is **not aggregated from municipalities**. It is read **directly from
> the GADM ADM2 GeoPackage** (`bolivia_adm2_gdp_perCapita_1990_2024.gpkg`) — whose ADM2 units already
> *are* the 112 provinces — and attached as-is by `build_gdp()` (no weighting, no aggregation). This is
> the one folder whose values are not produced by the population-weighted pipeline. See **How this data
> was generated** below and the [province aggregation report](../province_aggregation_report.md).

## Current Status

This directory provides a long-run panel of GDP per capita estimates:

- **[gdp_perCapita_1990_2024.csv](gdp_perCapita_1990_2024.csv)** - Annual GDP per capita for the 112 provinces, 1990-2024.

Additional GDP-related information can be found in:

- **[Interactive Dashboard](https://carlos-mendez.projects.earthengine.app/view/geoexplorer1v100bolivia)** - Visualizes GDP estimates along with other indicators

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

## How this data was generated

**Attached, not aggregated.** Unlike every other folder, these values are **already province-level in
the source** and are copied across unchanged — there is **no municipal→province aggregation and no
population weighting**. `build_gdp()` in [`../code/build_bolivia112.py`](../code/build_bolivia112.py):

1. Reads the GADM ADM2 GeoPackage `bolivia_adm2_gdp_perCapita_1990_2024.gpkg` (in [`../maps/`](../maps/)
   or the repo root) — its ADM2 polygons are the 112 provinces, each carrying annual GDP-per-capita
   fields for 1990–2024.
2. Matches each polygon to `prov_id` by its `(dep_id, normalized province name)`.
3. Renames the year columns to `gdppc1990 … gdppc2024` and writes the table.

> ⚠️ **Original GDP source and estimation method are not documented in this repo.** The figures arrive
> pre-computed inside the GeoPackage; how they were produced (e.g. satellite proxies, downscaling of
> national accounts, surveys) is **not recorded here** — treat the methodology as unverified. The
> reference below is a *general* method paper, **not** the source of these specific numbers.

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

General methodology reference for satellite-based GDP estimation — **not** the source of these
specific figures (which is undocumented in the repo, see above):

- [Henderson, J. V., Storeygard, A., & Weil, D. N. (2012). Measuring economic growth from outer space](https://www.aeaweb.org/articles?id=10.1257/aer.102.2.994)
- Main project README: [Data Integration Examples](../README.md)
