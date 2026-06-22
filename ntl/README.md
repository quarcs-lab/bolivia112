# Night-Time Lights (NTL) Data

## Overview

This directory contains night-time lights (NTL) data for Bolivia's 112 provinces from 2012 to 2020. Night-time lights are a widely-used proxy for economic activity, electrification, and urbanization.

> **Note**: Each value is **log NTL per capita** (intensive). Province values are the **population-weighted mean of the municipal ln values**, weighted by the **year-matched** population (e.g. `ln_NTLpc2015` uses `pop2015`). See **How these variables were aggregated & generated** below and the [province aggregation report](../province_aggregation_report.md).

## Files

### ln_NTLpc.csv

Contains log-transformed night-time lights per capita for 9 years, plus trend-adjusted values.

## What are Night-Time Lights?

Night-time lights (NTL) data is captured by satellite sensors that detect artificial light emissions from Earth's surface at night. This data is valuable because:

- **Economic Proxy**: Strong correlation with GDP, income levels, and economic development
- **Urbanization Indicator**: Tracks urban expansion and electrification
- **High Temporal Resolution**: Annual or more frequent observations
- **Spatial Coverage**: Available for remote areas lacking traditional statistics

## How these variables were aggregated & generated

**Generated (original source → municipal series).**

- **VIIRS (Visible Infrared Imaging Radiometer Suite)** — the conventional NTL sensor for 2012–2020
  (**DMSP-OLS** for pre-2012 history).
- The municipal series are produced by two Stata scripts: cleaning + Hodrick-Prescott trend in
  [`../code/archive_stata_code/030_clean_and_estimate_NTL_trends.do`](../code/archive_stata_code/030_clean_and_estimate_NTL_trends.do),
  then per-capita + log transform in
  [`../code/archive_stata_code/060_compute_NTL_pc.do`](../code/archive_stata_code/060_compute_NTL_pc.do).
  `bolivia112` consumes the municipal result from [`ds4bolivia`](https://github.com/quarcs-lab/ds4bolivia).

> ⚠️ The cleaning script reads a raw satellite export (`…/rawData/NTL/<hash>_results.csv`); the exact
> product/collection is **not re-stated in the script**. VIIRS is the standard product for this period
> but is not independently confirmed in the repo.

**Aggregated (municipality → province).** Each `ln_NTLpc*` / `ln_t400NTLpc*` is intensive and is
aggregated as the **population-weighted mean of the municipal *ln* values** (the average is taken on
the log scale directly, not on raw NTL), weighted by the **year-matched** population —
`ln_NTLpc2015` → `pop2015`, etc. (rule `wmean` with the year as weight in
[`../code/aggregation_rules.csv`](../code/aggregation_rules.csv), via `build_curated()` in
[`../code/build_bolivia112.py`](../code/build_bolivia112.py)).

## Variable Dictionary

| Variable Name | Description |
| --- | --- |
| **prov_id** | Province identifier (3-digit INE code) for joining datasets |
| **ln_NTLpc2012** | Natural logarithm of NTL per capita in 2012 (log-transformed intensity divided by population) |
| **ln_NTLpc2013** | Natural logarithm of NTL per capita in 2013 |
| **ln_NTLpc2014** | Natural logarithm of NTL per capita in 2014 |
| **ln_NTLpc2015** | Natural logarithm of NTL per capita in 2015 |
| **ln_NTLpc2016** | Natural logarithm of NTL per capita in 2016 |
| **ln_NTLpc2017** | Natural logarithm of NTL per capita in 2017 |
| **ln_NTLpc2018** | Natural logarithm of NTL per capita in 2018 |
| **ln_NTLpc2019** | Natural logarithm of NTL per capita in 2019 |
| **ln_NTLpc2020** | Natural logarithm of NTL per capita in 2020 |
| **ln_t400NTLpc2012** | Trend component of log NTL per capita in 2012 (HP-filtered with λ=400) |
| **ln_t400NTLpc2013** | Trend component of log NTL per capita in 2013 |
| **ln_t400NTLpc2014** | Trend component of log NTL per capita in 2014 |
| **ln_t400NTLpc2015** | Trend component of log NTL per capita in 2015 |
| **ln_t400NTLpc2016** | Trend component of log NTL per capita in 2016 |
| **ln_t400NTLpc2017** | Trend component of log NTL per capita in 2017 |
| **ln_t400NTLpc2018** | Trend component of log NTL per capita in 2018 |
| **ln_t400NTLpc2019** | Trend component of log NTL per capita in 2019 |
| **ln_t400NTLpc2020** | Trend component of log NTL per capita in 2020 |

## Data Transformations

### Log Transformation (ln_NTLpc)
- Raw NTL values are right-skewed, so natural logarithm normalization is applied
- Per capita adjustment controls for population size differences
- Formula: `ln_NTLpc = log(NTL_total / population)`

### Trend Component (ln_t400NTLpc)
- Hodrick-Prescott (HP) filter with smoothing parameter λ=400
- Extracts long-term trend from the time series
- Removes short-term fluctuations and cyclical variations
- Useful for analyzing structural economic changes vs. temporary shocks

## Usage

This dataset is used for:

- **Economic Growth Analysis**: Track changes in economic activity over time
- **Convergence Studies**: Compare development trajectories across provinces
- **GDP Estimation**: Use as predictor or validation for GDP models
- **Electrification Monitoring**: Track expansion of electricity access
- **Spatial Econometrics**: Analyze spatial spillovers in economic development

## Example Code

You can run the examples below in [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/notebooks/empty.ipynb)

```python
import pandas as pd
import matplotlib.pyplot as plt

# Load NTL data
url = "https://raw.githubusercontent.com/quarcs-lab/bolivia112/main/ntl/ln_NTLpc.csv"
df_ntl = pd.read_csv(url)

# Calculate growth rate (2012-2020)
df_ntl['growth_rate'] = ((df_ntl['ln_NTLpc2020'] - df_ntl['ln_NTLpc2012']) / 8) * 100

# Identify high-growth provinces
high_growth = df_ntl[df_ntl['growth_rate'] > df_ntl['growth_rate'].quantile(0.75)]

# Plot time series for a specific province
years = range(2012, 2021)
ntl_cols = [f'ln_NTLpc{year}' for year in years]
province_data = df_ntl.loc[0, ntl_cols]

plt.plot(years, province_data)
plt.xlabel('Year')
plt.ylabel('Log NTL per capita')
plt.title('Night-Time Lights Trend')
plt.show()
```

## Join Key

Use `prov_id` to join this dataset with other datasets in the repository.

## Processing Scripts

Municipal series: [`../code/archive_stata_code/030_clean_and_estimate_NTL_trends.do`](../code/archive_stata_code/030_clean_and_estimate_NTL_trends.do)
and [`../code/archive_stata_code/060_compute_NTL_pc.do`](../code/archive_stata_code/060_compute_NTL_pc.do).
Province aggregation (`wmean` of the ln values): [`../code/build_bolivia112.py`](../code/build_bolivia112.py).

## References

Methodology references (not the data source):

- Henderson, J. V., Storeygard, A., & Weil, D. N. (2012). Measuring economic growth from outer space. American Economic Review, 102(2), 994-1028.
- Elvidge, C. D., et al. (2017). VIIRS night-time lights. International Journal of Remote Sensing, 38(21), 5860-5879.
