# Code and Data Processing Scripts (bolivia112)

## Overview

This directory contains the data processing scripts and machine learning models used to construct datasets and perform poverty predictions in **bolivia112**, the province-level (112 provinces) replication of the municipal [ds4bolivia](https://github.com/quarcs-lab/ds4bolivia) repository. The scripts are organized by type and function.

> **Note:** `build_bolivia112.py` aggregates municipality → province as follows: **intensive** variables → population-weighted mean (SDGs by `pop2020`; others by year-matched `pop`); **extensive** variables → sum; GDP and geometry → attached as-is. The per-variable rule for every column lives in [`aggregation_rules.csv`](aggregation_rules.csv); see also the dataset summary in the [main README](../README.md) and the full [province aggregation report](../province_aggregation_report.md).

## Scripts Overview

### Python Scripts - Province Aggregation

#### build_bolivia112.py

Builds the entire `bolivia112` dataset by aggregating the 339 municipal tables of `ds4bolivia` into 112 provinces. This is the core pipeline that produces every province-level CSV and the master file, keyed by `prov_id` (the first 3 digits of the INE `mun_id`, e.g. `405` = Litoral).

**Functionality:**
- Aggregates municipal data to provinces using **population-weighted aggregation** (intensive variables = weighted mean, extensive variables = sum; `min`/`max` companions kept as min/max)
- Weights **all** variables by the INE `pop/pop.csv` series — SDG-related variables by `pop2020`, all others year-matched — and sets the `population_2020` column to INE pop2020 (= Σ municipal `pop2020`)
- Imputes all-NaN SDG cells with the pop-weighted department mean and flags them via `<var>_imputed` columns
- Reproduces every province CSV with the same filenames and column schemas as `ds4bolivia`
- Recomputes derived fields (e.g. `rank_imds`) at the province level
- Idempotent: re-running reproduces the same outputs

**Aggregation rules:** the per-variable rules (aggregation method and weight) are recorded in [aggregation_rules.csv](aggregation_rules.csv).

**Usage:**
```bash
uv run python code/build_bolivia112.py
```

---

### Python Scripts - Data Processing

#### satellite_data_merger.py

Merges satellite-derived datasets (embeddings, NTL, land cover) with socio-economic indicators at the province level. Handles spatial joins and data alignment.

**Functionality:**
- Merges satellite embeddings with SDG data on `prov_id`
- Handles spatial data alignment
- Exports merged datasets for analysis

**Usage:**
```bash
python code/satellite_data_merger.py
```

---

### Python Scripts - Machine Learning Models

> The performance metrics and feature rankings below were originally established on the 339-municipality data of `ds4bolivia`. When re-run on the 112 population-weighted provinces, the exact numbers will differ; treat the values here as indicative of model behavior and the typical urban/rural error structure.

#### run_poverty_prediction.py

**Predicting General Poverty (SDG 1) Using Random Forest**

Predicts the SDG 1 Index (No Poverty) using 64-dimensional satellite imagery embeddings.

**Key Features:**
- Random Forest regression with 500 trees
- 5-fold cross-validation
- Feature importance analysis
- Prediction error analysis by province
- Identifies overpredicted and underpredicted provinces

**Performance:**
- Cross-validation R²: 0.3614 (±0.0685)
- Test R²: 0.4025
- Test RMSE: 17.48 percentage points
- Test MAE: 13.33 percentage points

**Top 5 Features:** A43, A59, A13, A07, A04

**Usage:**
```bash
python code/run_poverty_prediction.py
```

---

#### run_energy_prediction.py

**Predicting Energy Poverty (SDG 7 Index) Using Random Forest**

Predicts the SDG 7 Index (Affordable and Clean Energy) using satellite embeddings.

**Key Features:**
- Comparison with SDG 1 (general poverty) patterns
- Correlation analysis: SDG 1 vs SDG 7 = 0.9197
- Identifies provinces with unique energy access patterns
- Analyzes urban vs rural disparities

**Performance:**
- Cross-validation R²: 0.2482 (±0.0978)
- Test R²: 0.3507
- Test RMSE: 13.43 percentage points
- Test MAE: 10.03 percentage points

**Top 5 Features:** A13, A57, A59, A21, A52

**Usage:**
```bash
python code/run_energy_prediction.py
```

---

#### run_extreme_energy_poverty.py ⭐ **Recommended**

**Predicting Extreme Energy Poverty Rate Using Random Forest**

Predicts `sdg1_1_eepr` - the percentage of houses in extreme energy poverty (2016). This uses a **direct measurement** rather than composite indices.

**Why This Model?**
- Direct measurement: % of houses in extreme energy poverty
- Better cross-validation performance (R² = 0.57)
- Policy relevant: Directly actionable for electrification programs
- Clear interpretation: Easy to communicate findings

**Key Features:**
- Analysis of provinces with available data
- Correlation with related poverty indicators
- Identifies systematic urban/rural prediction errors
- Only 36/64 features (56%) needed for 80% importance

**Performance:**
- Cross-validation R²: 0.5704 (±0.0823)
- Test R²: 0.2216
- Test RMSE: 21.51 percentage points
- Test MAE: 15.52 percentage points

**Top 5 Features:** A43, A25, A23, A61, A62

**Critical Findings:**
- Urban centers systematically overpredicted (e.g. La Paz, Quillacollo)
- Rural extreme poverty underpredicted (e.g. Cocapata)
- Strong correlation with unsatisfied basic needs (r = 0.80)
- Negative correlation with electricity coverage (r = -0.66)

**Usage:**
```bash
python code/run_extreme_energy_poverty.py
```

---

#### run_imds_prediction.py

**Predicting the Sustainable Development Index (IMDS) Using Random Forest**

Predicts the IMDS - a composite index aggregating all SDG indicators into a single province development score.

**Key Features:**
- Analysis of 112 provinces (no missing IMDS data)
- 5-fold cross-validation
- Feature importance analysis across 64 satellite embeddings
- Identifies urban-rural prediction patterns

**Performance:**
- Cross-validation R²: 0.2288 (±0.0292)
- Test R²: 0.2284
- Test RMSE: 6.53 IMDS points
- Test MAE: 4.75 IMDS points

**Top 5 Features:** A30, A59, A57, A13, A26

**Critical Findings:**
- Urban centers systematically underpredicted (e.g. Murillo / La Paz)
- Rural highlands overpredicted (e.g. Tomás Frías / Tinguipaya area)
- 44/64 features (68.8%) needed for 80% importance
- Composite indices harder to predict than specific indicators

**Usage:**
```bash
python code/run_imds_prediction.py
```

**Documentation:** [run_imds_prediction.md](run_imds_prediction.md)

---

### Stata Scripts (.do files) — upstream lineage

These Stata scripts live in the upstream municipal repository [ds4bolivia](https://github.com/quarcs-lab/ds4bolivia). They build the original 339-municipality tables, which `build_bolivia112.py` then aggregates to the 112 provinces. They are documented here for provenance.

| Script | Description |
| --- | --- |
| **010_add_poly_id_and____.do** | Adds spatial identifiers to datasets (province tables instead use `prov_id` as the join key) |
| **020_create_regional_identifiers_dataset.do** | Creates the regionNames dataset with administrative metadata (provinces, departments, IDs) |
| **030_clean_and_estimate_NTL_trends.do** | Cleans and estimates time trends for night-time lights (NTL) data across provinces |
| **040_clean_and_estimate_Population_trends.do** | Processes population data and estimates temporal trends (2001-2020) |
| **050_clean_and_estimate_CO2_trends.do** | Cleans and estimates CO2 emissions trends from satellite data |
| **060_compute_NTL_pc.do** | Computes night-time lights per capita (NTL/population) for economic analysis |
| **070_combine_SDGs_lnNTLpc_POP_CO2.do** | Merges SDG indicators with log NTL per capita, population, and CO2 data into master dataset |
| **080_translate_and_selectVariables.do** | Translates variable names from Spanish to English and selects final variables for publication |
| **save_variable_names_and_labes_as_CSV_file.do** | Exports variable metadata (names and labels) to CSV for documentation |

---

### JavaScript Scripts (.js files)

Google Earth Engine (GEE) scripts for processing satellite imagery at scale.

| Script | Description |
| --- | --- |
| **aggregate-satellite-embedings-to-adm.js** | Aggregates Google Satellite Embeddings from 10m resolution to administrative boundaries using spatial mean reduction. Generates the 64-dimensional feature vectors; in `bolivia112` these are then population-weighted to the province level. See detailed documentation in [satelliteEmbeddings/README.md](../satelliteEmbeddings/README.md) |

---

## Data Processing Workflow

The scripts follow this general sequence:

1. **Spatial Identifiers** (010, 020): Create unique IDs and administrative metadata
2. **Time Series Processing** (030-050): Clean and estimate trends for satellite-derived variables
3. **Derived Variables** (060): Compute per capita metrics and transformations
4. **Data Integration** (070, satellite_data_merger.py): Merge multiple data sources
5. **Finalization** (080): Translate, select, and document final variables
6. **Province Aggregation** (build_bolivia112.py): Population-weighted aggregation of the 339 municipal tables into the 112 province tables, keyed by `prov_id` (this is the step that produces `bolivia112`)
7. **Machine Learning** (run_*.py): Train models and predict poverty indicators

---

## Output Datasets

These scripts generate the province-level CSV files (each keyed by `prov_id`) found in:

- [regionNames/](../regionNames/) - Administrative identifiers (`prov_id`, `prov`, `capital`, `dep`, `dep_id`, `dep_prov`, `n_mun`, `gadm_name`, `sources`)
- [sdg/](../sdg/) - SDG composite indices (`imds`, `index_sdg1`..`index_sdg17`)
- [sdgVariables/](../sdgVariables/) - Detailed SDG variables (`population_2020`, `urbano_2012`, `sdg*`...)
- [pop/](../pop/) - Population time series (`pop2001`..`pop2020`)
- [ntl/](../ntl/) - Night-time lights data (`ln_NTLpc2012`..`2020`, `ln_t400NTLpc2012`..`2020`)
- [satelliteEmbeddings/](../satelliteEmbeddings/) - 64-dimensional satellite feature vectors (`A00`..`A63`)
- [gdp/](../gdp/) - GDP per capita 1990-2024 (`gdppc1990`..`gdppc2024`)
- [datasets/](../datasets/) - Merged analytical datasets (`sdgs_satelliteEmbeddings2017.csv`)
- Master files: [`../bolivia112_v20260622.csv`](../bolivia112_v20260622.csv) and [`../definitions_bolivia112_v20260622.csv`](../definitions_bolivia112_v20260622.csv)

Every table has **112 rows** (one per province) and is keyed by `prov_id`. The municipal-only identifier columns (`poly_id`, `asdf_id`, `mun_id`, `shapeID`, `dep_mun`) do **not** exist in the province tables; use `prov_id` as the single join key (and `dep_prov` for the department-province label). Province values are population-weighted aggregations of the municipal data (intensive variables = weighted mean, extensive variables = sum); see [../province_aggregation_report.md](../province_aggregation_report.md).

---

## Province Schema (data dictionary)

| File | Key | Other columns |
| --- | --- | --- |
| `regionNames/regionNames.csv` | `prov_id` | `prov`, `capital`, `dep`, `dep_id`, `dep_prov`, `n_mun`, `gadm_name`, `sources` |
| `sdg/sdg.csv` | `prov_id` | `imds`, `index_sdg1`..`index_sdg17` |
| `sdgVariables/sdgVariables.csv` | `prov_id` | `population_2020`, `urbano_2012`, `sdg*`... |
| `pop/pop.csv` | `prov_id` | `pop2001`..`pop2020` |
| `ntl/ln_NTLpc.csv` | `prov_id` | `ln_NTLpc2012`..`2020`, `ln_t400NTLpc2012`..`2020` |
| `satelliteEmbeddings/satelliteEmbeddings2017.csv` | `prov_id` | `A00`..`A63` |
| `datasets/sdgs_satelliteEmbeddings2017.csv` | `prov_id` | `prov`, `dep`, `dep_id`, `dep_prov`, `imds`, `index_sdg1`..`17`, `A00`..`A63` |
| `gdp/gdp_perCapita_1990_2024.csv` | `prov_id` | `prov`, `dep`, `dep_id`, `gdppc1990`..`gdppc2024` |

Maps: `maps/bolivia112provincesOpt.geojson` and `maps/bolivia112provincesFull.geojson` (112 features; properties `prov_id`, `prov`, `dep`, `dep_id`, `shapeName`, `COORD_X`, `COORD_Y`).

**Example — load and merge province data on `prov_id`:**
```python
import pandas as pd

base = "bolivia112"  # local repo path; or
# base = "https://raw.githubusercontent.com/quarcs-lab/bolivia112/main"

sdg = pd.read_csv(f"{base}/sdg/sdg.csv")                                    # prov_id, imds, index_sdg1..17
emb = pd.read_csv(f"{base}/satelliteEmbeddings/satelliteEmbeddings2017.csv")  # prov_id, A00..A63

df = pd.merge(sdg, emb, on="prov_id", how="inner")
assert len(df) == 112  # 112 provinces
```

---

## Requirements

### Python
```bash
# Core libraries
pandas
numpy

# Spatial data
geopandas

# Machine learning
scikit-learn
matplotlib
seaborn
```

### Stata (upstream municipal lineage only)
- Stata 15 or higher
- Access to the raw municipal data files in [ds4bolivia](https://github.com/quarcs-lab/ds4bolivia)

### Google Earth Engine
- GEE account (free for research/education)
- Access to Bolivia administrative boundaries asset
- GEE Python API or Code Editor

---

## Running the Scripts

### Build the province dataset

```bash
# Aggregate the 339 municipal tables into the 112 province tables
uv run python code/build_bolivia112.py
```

### Python Scripts - Data Processing

```bash
python code/satellite_data_merger.py
```

### Python Scripts - Machine Learning

```bash
# Poverty prediction (SDG 1)
python code/run_poverty_prediction.py

# Energy poverty (SDG 7 Index)
python code/run_energy_prediction.py

# Extreme energy poverty rate (Recommended)
python code/run_extreme_energy_poverty.py
```

### Stata Scripts (upstream, in ds4bolivia)

```stata
// Set working directory to the upstream municipal repository
cd "/path/to/ds4bolivia"

// Run scripts in sequence
do code/010_add_poly_id_and____.do
do code/020_create_regional_identifiers_dataset.do
// ... etc
```

### JavaScript/GEE Scripts

1. Open [Google Earth Engine Code Editor](https://code.earthengine.google.com/)
2. Copy and paste the script content
3. Update asset paths if necessary
4. Click "Run"
5. Export results to Google Drive

---

## Model Comparison Summary

| Model | Target Variable | Test R² | MAE | Key Insight |
|-------|----------------|---------|-----|-------------|
| **General Poverty** | index_sdg1 | 0.40 | ±13.3pp | Urban centers underpredicted |
| **Energy Poverty** | index_sdg7 | 0.35 | ±10.0pp | Strong correlation with SDG 1 (r=0.92) |
| **Extreme Energy Poverty** ⭐ | sdg1_1_eepr | 0.22 (CV: 0.57) | ±15.5pp | Best CV performance, clearest interpretation |

**Recommendation:** Use `run_extreme_energy_poverty.py` for most analyses due to direct measurement and better cross-validation performance.

---

## Project Documentation

For more information about the research project and methodology:

- **Video Introduction**: [Project Overview](https://www.loom.com/share/07206f02b269485293ac7c8ad4df3c7f)
- **Computational Environment**: [Deepnote Notebooks](https://deepnote.com/project/project2021o-Bolivia-esda-HABNFWMYQ8CWOKKwDrJrTQ)

---

## Collaborators

- Carlos Mendez (carlos@gsid.nagoya-u.ac.jp, Nagoya University)
- Erick Gonzales (erick.gonzalesrocha@un.org, United Nations Office for Disaster Risk Reduction)
- Pedro Leoni (pedroleoni1605@gmail.com)

---

## References

- [Anselin, L., Sridharan, S., & Gholston, S. (2007). Using exploratory spatial data analysis to leverage social indicator databases](https://kami.app/NduBfCB3hNln)
- [Mendez, C., & Gonzales, E. (2021). Human Capital Constraints, Spatial Dependence, and Regionalization in Bolivia](https://doi.org/10.18800/economia.202101.007)
- [Geographic Data Science with Python](https://geographicdata.science/book/intro.html)
- [GeoDa Workbook](https://geodacenter.github.io/documentation.html)

---

## Data Sources

- [Andersen, L. E., Canelas, S., Gonzales, A., Peñaranda, L. (2020) Atlas Municipal de los ODS Bolivia 2020](https://atlas.sdsnbolivia.org)
- Municipal source repository: [ds4bolivia](https://github.com/quarcs-lab/ds4bolivia) — province values are population-weighted aggregations of these municipal data (see [../province_aggregation_report.md](../province_aggregation_report.md))

---

## Citation

```
Mendez, C., Gonzales, E., Leoni, P., Andersen, L., Peralta, H. (2026).
bolivia112: A Province-Level Data Science Repository to Study GeoSpatial
Development in Bolivia [Data set]. GitHub. https://github.com/quarcs-lab/bolivia112
```
