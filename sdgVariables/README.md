# SDG Variables - Detailed Indicators

## Overview

This directory contains detailed Sustainable Development Goal (SDG) variables for Bolivia's 112 provinces. Unlike the aggregated SDG indices in [sdg/](../sdg/), this dataset includes the underlying individual indicators that compose each SDG index, providing granular data for in-depth analysis.

> **Note:** Province values are population-weighted aggregations of the underlying municipal data, weighted by INE `pop2020` (intensive variables = weighted mean, extensive variables = sum). `population_2020` is the INE 2020 population (= Σ municipal `pop2020`, consistent with `pop/pop.csv`). See [../province_aggregation_report.md](../province_aggregation_report.md) for details.

## Files

### sdgVariables.csv

Contains 64 detailed SDG variables plus population and urbanization data for all 112 provinces. Five
`<var>_imputed` boolean flag columns mark province cells that were imputed because *all* their
municipalities lacked that indicator (see **Missing values** below).

## Variable Dictionary

The core columns aggregate differently from the SDG indicators, so their rule is shown explicitly:

| Variable Name | Description | Aggregation (municipality → province) |
| --- | --- | --- |
| **prov_id** | Province identifier (3-digit INE code) for joining datasets | province key (first 3 digits of `mun_id`) |
| **population_2020** | Population 2020 (INE; = Σ municipal `pop2020`, consistent with `pop/pop.csv`) | **set to INE `pop2020`** (sum of municipal `pop2020`) |
| **urbano_2012** | Urbanization rate, 2012 (% of population) | population-weighted mean · `pop2020` |

> **All `sdg*` indicators listed below** share one rule — **population-weighted mean weighted by
> `pop2020`** (`prov = Σ xᵢ·pop2020ᵢ / Σ pop2020ᵢ`). The only exceptions are the five indicators that
> are fully missing for some province and are therefore **imputed** (each carries a companion
> `<var>_imputed` flag): `sdg1_1_eepr`, `sdg8_4_rem`, `sdg10_2_iec`, `sdg2_4_pual`, `sdg2_4_td` — see
> **Missing values & imputation** in the Notes. The per-variable rules are also machine-readable in
> [`../code/aggregation_rules.csv`](../code/aggregation_rules.csv).

### SDG 1: No Poverty

| Variable Name | Description |
| --- | --- |
| **sdg1_1_eepr** | Extreme energy poverty rate, 2016 (% of houses) |
| **sdg1_1_ubn** | Unsatisfied basic needs, 2012 (% of population) |
| **sdg1_2_mpi** | Multidimensional poverty index, 2012 |
| **sdg1_4_abs** | Access to the 3 basic services, 2012 (% of households) |

### SDG 2: Zero Hunger

| Variable Name | Description |
| --- | --- |
| **sdg2_2_cmc** | Chronic malnutrition in children (< 5 years), 2016 (%) |
| **sdg2_2_oww** | Obesity in women (15-49 years), 2016 (%) |
| **sdg2_4_pual** | Average area per Production Unit Agriculture and Livestock, 2013 (ha) |
| **sdg2_4_td** | Tractor density, 2013 (per 1,000 UPAs) |

### SDG 3: Good Health and Well-being

| Variable Name | Description |
| --- | --- |
| **sdg3_1_idca** | Institutional childbirth coverage, average 2008-2012 (%) |
| **sdg3_2_imr** | Infant mortality rate (< 1 year), 2016 (per 1,000 live births) |
| **sdg3_2_mrc** | Children mortality rate (< 5 years), 2016 (per 1,000 live births) |
| **sdg3_3_cdir** | Chagas disease infestation rate, 2017 (% of households) |
| **sdg3_3_di** | Dengue incidence, 2018 (per 10,000 population) |
| **sdg3_3_imr** | Malaria incidence, average 2014-17 (per 1,000 population) |
| **sdg3_3_ti** | Tuberculosis incidence, 2017 (per 100,000 population) |
| **sdg3_3_hivi** | HIV incidence, average 2014-17 (per 1,000,000 population) |
| **sdg3_7_afr** | Adolescent fertility rate (15-19 years), 2012 (births per 1,000 women) |

### SDG 4: Quality Education

| Variable Name | Description |
| --- | --- |
| **sdg4_1_ssdrm** | Secondary school dropout rate, male, 2017 (% of enrolled) |
| **sdg4_1_ssdrf** | Secondary school dropout rate, female, 2017 (% of enrolled) |
| **sdg4_4_phe** | Population with higher education (>= 19 years), 2012 (%) |
| **sdg4_6_lr** | Literacy rate (>= 15 years), 2012 (%) |
| **sdg4_c_qti** | Qualified teachers at the initial level, 2016 (%) |
| **sdg4_c_qts** | Qualified teachers at the secondary level, 2016 (%) |

### SDG 5: Gender Equality

| Variable Name | Description |
| --- | --- |
| **sdg5_1_gpsd** | Gender parity in school dropouts in secondary school, 2017 |
| **sdg5_1_gpyp** | Gender parity in years of education of young people (25-35 years old), 2012 |
| **sdg5_1_gpmpi** | Gender Parity in the Multidimensional Poverty Index, 2012 |
| **sdg5_5_gpop** | Gender parity in the overall participation rate (>= 10 years), 2012 |

### SDG 6: Clean Water and Sanitation

| Variable Name | Description |
| --- | --- |
| **sdg6_1_dwc** | Drinking water coverage, 2017 (% of population) |
| **sdg6_2_sc** | Sanitation coverage, 2017 (% of population) |
| **sdg6_3_wwt** | Wastewater treatment, 2017 (% of wastewater) |

### SDG 7: Affordable and Clean Energy

| Variable Name | Description |
| --- | --- |
| **sdg7_1_ec** | Electricity coverage, 2012 (% of population) |
| **sdg7_1_rec** | Residential electricity consumption per capita, 2016 (kWh/person/year) |
| **sdg7_1_cce** | Clean cooking energy, 2012 (% of households) |
| **sdg7_3_co2epc** | CO2 emissions per capita by energy, 2016 (tCO2/person/year) |

### SDG 8: Decent Work and Economic Growth

| Variable Name | Description |
| --- | --- |
| **sdg8_4_rem** | Residential electric meters with zero consumption, 2016 (%) |
| **sdg8_5_oprm** | Overall participation rate males (>= 10 years), 2012 (%) |
| **sdg8_5_ofrm** | Overall female participation rate (>= 10 years), 2012 (%) |
| **sdg8_6_mlm** | Men who do not study or participate in the labor market (15-24 years), 2012 (%) |
| **sdg8_6_wlm** | Women who do not study or participate in the labor market (15-24 years), 2012 (%) |
| **sdg8_10_dbb** | Density of bank branches, 2018 (per 100,000 inhabitants) |
| **sdg8_11_idi** | Index of the degree of intermediation in migration, 2012 |

### SDG 9: Industry, Innovation and Infrastructure

| Variable Name | Description |
| --- | --- |
| **sdg9_1_routes** | Number of railways/primary roads entering/leaving the province, 2019 |
| **sdg9_5_cd** | Kuaa computers delivered, 2016 (per 100 school-age population, 6-19 years) |
| **sdg9_5_eutf** | Educational units with technological floors, 2016 (%) |
| **sdg9_c_mnc** | Fixed and mobile network coverage, 2012 (% of households) |
| **sdg9_c_drb** | Density of radio bases, 2016 (number of radio bases per 1,000 inhabitants) |

### SDG 10: Reduced Inequalities

| Variable Name | Description |
| --- | --- |
| **sdg10_2_gcye** | GINI coefficient of years of education, 2012 |
| **sdg10_2_iec** | Inequality in electricity consumption, 2016 |
| **sdg10_2_nssp** | Non-Spanish speaking population (>= 3 years), 2012 (%) |

### SDG 11: Sustainable Cities and Communities

| Variable Name | Description |
| --- | --- |
| **sdg11_1_hocr** | Overcrowding rate, 2012 (% of households) |
| **sdg11_1_hno** | Households that do not have a toilet, bathroom or latrine, 2012 (%) |
| **sdg11_2_samt** | Seats available for mass transit, 2017 (per 1,000 inhabitants) |

### SDG 13: Climate Action

| Variable Name | Description |
| --- | --- |
| **sdg13_1_ccvi** | Climate change vulnerability Index, 2015 |
| **sdg13_2_tco2e** | Total CO2 emissions per capita, 2016 (tCO2/person/year) |
| **sdg13_2_dra** | Deforestation rate, average 2016-2018 (% of forest area 2015) |

### SDG 15: Life on Land

| Variable Name | Description |
| --- | --- |
| **sdg15_1_pa** | Protected areas, 2019 (% of the province's land area) |
| **sdg15_5_blr** | Biodiversity loss rate due to deforestation, average 2016-2018 |

### SDG 16: Peace, Justice and Strong Institutions

| Variable Name | Description |
| --- | --- |
| **sdg16_1_rhr** | Registered homicide rate, average 2015-2017 (per 100,000 inhabitants) |
| **sdg16_6_pbec** | Programmed budget execution capacity, 2017 (%) |
| **sdg16_9_cr** | Children registered in the civil registry (< 5 years), 2012 (%) |

### SDG 17: Partnerships for the Goals

| Variable Name | Description |
| --- | --- |
| **sdg17_1_pmtax** | Proportion of provincial revenues that come from local taxes, 2017 (%) |
| **sdg17_5_pipc** | Public investment per capita, 2017 (Bs./person) |

## Usage

This dataset is used for:

- **Detailed SDG Analysis**: Examine specific indicators that drive overall SDG performance
- **Policy Targeting**: Identify specific areas of intervention (e.g., which health indicators need improvement)
- **Comparative Studies**: Compare provinces on specific metrics rather than aggregated indices
- **Correlation Analysis**: Study relationships between specific variables across SDGs
- **Machine Learning**: Use granular variables as features for predictive models

## Example Code

You can run the examples below in [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/notebooks/empty.ipynb)

```python
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load detailed SDG variables
url = "https://raw.githubusercontent.com/quarcs-lab/bolivia112/main/sdgVariables/sdgVariables.csv"
df_sdg_vars = pd.read_csv(url)

# Examine poverty indicators
poverty_vars = ['sdg1_1_eepr', 'sdg1_1_ubn', 'sdg1_2_mpi', 'sdg1_4_abs']
df_poverty = df_sdg_vars[['prov_id'] + poverty_vars]

# Calculate correlation between poverty indicators
corr_matrix = df_poverty[poverty_vars].corr()
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm')
plt.title('Correlation between SDG 1 Poverty Indicators')
plt.show()

# Identify provinces with high malnutrition
high_malnutrition = df_sdg_vars[df_sdg_vars['sdg2_2_cmc'] > 30]
print(f"Provinces with >30% chronic malnutrition: {len(high_malnutrition)}")

# Compare gender parity across indicators
gender_parity_vars = [col for col in df_sdg_vars.columns if 'sdg5' in col]
df_gender = df_sdg_vars[['prov_id'] + gender_parity_vars]
```

## How these variables were aggregated & generated

**Generated (original source → municipal indicator).** The granular SDG indicators are constructed at
the **municipal** level (339 municipalities) by the *Atlas Municipal de los Objetivos de Desarrollo
Sostenible en Bolivia 2020*:

> Andersen, L. E., Canelas, S., Gonzales, A., Peñaranda, L. (2020). *Atlas municipal de los Objetivos
> de Desarrollo Sostenible en Bolivia 2020.* La Paz: Universidad Privada Boliviana, SDSN Bolivia.
> [https://atlas.sdsnbolivia.org](https://atlas.sdsnbolivia.org)

`bolivia112` consumes these municipal indicators from
[`ds4bolivia`](https://github.com/quarcs-lab/ds4bolivia).

**Aggregated (municipality → province).** Performed by `build_curated()` in
[`../code/build_bolivia112.py`](../code/build_bolivia112.py):

- All `sdg*` indicators and `urbano_2012` → **population-weighted mean weighted by `pop2020`** (rule
  `wmean`, weight `2020`).
- `population_2020` → **set to INE `pop2020`** (the sum of municipal `pop2020`), so it matches
  [`../pop/pop.csv`](../pop/README.md).
- Province cells with **no municipal data at all** are **imputed** from the department's pop-weighted
  mean and flagged — see **Missing values & imputation** in the Notes.

Full method: [../province_aggregation_report.md](../province_aggregation_report.md).

## Aggregation caveats (statistical)

A statistician's audit of this aggregation is in
[`../sdg_aggregation_audit.md`](../sdg_aggregation_audit.md). Key points for users:

- **Weights are approximate for many indicators.** 36 of 62 indicators are rates whose true
  denominator is *not* total population (households, children, women, enrolled pupils, land/forest
  area, …) yet are population-weighted by `pop2020`. Check
  [`sdg_reference_populations.csv`](sdg_reference_populations.csv) — the `weight_is_approximate` flag
  marks these — and [`../code/sdg_aggregation_sensitivity.csv`](../code/sdg_aggregation_sensitivity.csv)
  to see which are also empirically weight-sensitive.
- **Areal rates are area-weighted** (`sdg15_1_pa`, `sdg13_2_dra`, `sdg15_5_blr`), not pop-weighted —
  exact for `sdg15_1_pa`, a land-area proxy for the two forest rates.
- **Imputed cells** (`<var>_imputed = True`) are synthetic — exclude them from inferential/spatial
  models or model the flag.
- **Low support / single-municipality provinces:** some province values rest on one municipality; see
  the audit for the support diagnostics.

## Relationship to Other Datasets

- **[sdg/](../sdg/)** - Contains aggregated SDG indices (composite scores)
- **[regionNames/](../regionNames/)** - Administrative names for provinces
- **[datasets/](../datasets/)** - Merged datasets including SDG indices and satellite data

## Join Key

Use `prov_id` (3-digit INE province code) to join this dataset with other datasets in the repository.

## Notes

- Province values are population-weighted aggregations of the underlying municipal data, weighted by INE `pop2020` (intensive variables = weighted mean, extensive variables = sum); see [../province_aggregation_report.md](../province_aggregation_report.md)
- This dataset provides the granular indicators that compose the SDG indices
- **Missing values & imputation:** where only *some* municipalities lack an indicator, the weighted mean simply renormalizes over those with data. Where *all* municipalities of a province lack an indicator, the province value is **imputed** with the pop-weighted mean of the same department's provinces that have data, and the `<var>_imputed` flag is set to `True`. Eight cells are imputed: `sdg1_1_eepr`, `sdg8_4_rem`, `sdg10_2_iec` for **904 (Abuná)** & **905 (Federico Román)** (Pando); `sdg2_4_pual`, `sdg2_4_td` for **301 (Cercado, Cochabamba)**. To analyze only observed data, filter out rows where the relevant `<var>_imputed` is `True`.
- Years of measurement vary by indicator (2012-2019)
- Units and scales differ across variables - always check the description
