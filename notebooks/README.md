# Computational Notebooks

## Overview

This directory contains Jupyter notebooks with step-by-step tutorials for exploratory spatial data analysis (ESDA), machine learning, and poverty prediction using Bolivia's provincial development data and satellite imagery.

**Note:** All province values are population-weighted aggregations of the municipal data (intensive variables = weighted mean, extensive variables = sum). See [../province_aggregation_report.md](../province_aggregation_report.md) for details.

## Files

### Spatial Analysis Notebooks

#### eda.ipynb

**Exploratory Data Analysis (EDA)**

Descriptive statistics, regional comparisons, population treemaps, and the relationship between nighttime lights and development across 112 provinces.

**Run in Google Colab:**

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/quarcs-lab/bolivia112/blob/main/notebooks/eda.ipynb)

#### esda.ipynb

**Exploratory Spatial Data Analysis (ESDA)**

An interactive tutorial demonstrating spatial analysis techniques using Bolivia's SDG data. This notebook is designed for researchers and students learning spatial econometrics and geographic data science.

**Topics Covered:**
- Global spatial autocorrelation (Moran's I)
- Local spatial autocorrelation (LISA statistics)
- Spatial clustering and outlier detection
- Choropleth mapping
- Spatial weights matrices

**Run in Google Colab:**

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/quarcs-lab/bolivia112/blob/main/notebooks/esda.ipynb)

#### esda_dependence.ipynb

**Spatial Distribution & Dependence**

Map classification schemes (BoxPlot, Fisher-Jenks), spatial weights matrices, Global Moran's I, and LISA cluster analysis for detecting spatial autocorrelation patterns.

**Run in Google Colab:**

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/quarcs-lab/bolivia112/blob/main/notebooks/esda_dependence.ipynb)

#### esda_inequality.ipynb

**Spatial Inequality**

Theil index with between/within decomposition by department, Gini coefficient, and Spatial Gini index for measuring how much inequality is spatially structured.

**Run in Google Colab:**

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/quarcs-lab/bolivia112/blob/main/notebooks/esda_inequality.ipynb)

#### esda_heterogeneity.ipynb

**Spatial Heterogeneity (GWR & MGWR)**

Geographically Weighted Regression and Multiscale GWR to detect spatially varying relationships between nighttime lights and regional development.

**Run in Google Colab:**

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/quarcs-lab/bolivia112/blob/main/notebooks/esda_heterogeneity.ipynb)

#### eda_esda.ipynb

**Extended EDA + Spatial Analysis**

A comprehensive notebook combining traditional exploratory data analysis with spatial methods. Includes additional visualizations, statistical summaries, and advanced spatial analysis techniques.

**Run in Google Colab:**

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/quarcs-lab/bolivia112/blob/main/notebooks/eda_esda.ipynb)

---

## Prerequisites

To run these notebooks, you need:

```python
# Core libraries
pandas
numpy
matplotlib
seaborn

# Spatial analysis
geopandas
pysal
libpysal
esda
splot

# Machine learning
scikit-learn
```

## Jupytext and MyST Markdown

All notebooks are managed with [Jupytext](https://jupytext.readthedocs.io/) using [MyST Markdown](https://myst-parser.readthedocs.io/) as the source format. Each `.ipynb` file is paired with a `.md` file that serves as the human-readable, version-control-friendly source.

**Editing workflow:**

1. Edit the `.md` file (the source of truth)
2. Sync changes to the `.ipynb` file:

   ```bash
   uv run jupytext --sync notebooks/<notebook>.md
   ```

3. Or sync all notebooks at once:

   ```bash
   uv run jupytext --sync notebooks/*.md
   ```

**Opening `.md` files as notebooks:**

With Jupytext installed, Jupyter can open `.md` files directly as notebooks. You can also convert manually:

```bash
uv run jupytext --to notebook notebooks/<notebook>.md
```

**Note:** Both `.md` and `.ipynb` files are tracked in git. The `.md` files produce cleaner diffs for code review.

## Usage

You can run these notebooks in three ways:

1. **Google Colab** (Recommended): Click the badge above to run in the cloud without installation
2. **Local Jupyter**: Clone the repository and run `uv run jupyter notebook` in this directory
3. **Deepnote/Other Cloud Platforms**: Import the notebook files

**Note:** All notebooks include `!pip install` cells that install required spatial analysis packages. In Google Colab, these install packages not in Colab's default environment. When running locally with UV (`uv run jupyter notebook`), these commands are harmless since all packages are already installed via `pyproject.toml`.

## Learning Path

For best results, follow this sequence:

### For Spatial Analysis

1. Start with [eda.ipynb](eda.ipynb) for exploratory data analysis
2. Continue with [esda_dependence.ipynb](esda_dependence.ipynb) for spatial distribution and autocorrelation
3. Explore [esda_inequality.ipynb](esda_inequality.ipynb) for Theil and Gini inequality measures
4. Advance to [esda_heterogeneity.ipynb](esda_heterogeneity.ipynb) for GWR and MGWR
5. See [esda.ipynb](esda.ipynb) for an alternative ESDA tutorial
6. Review [eda_esda.ipynb](eda_esda.ipynb) for the comprehensive combined notebook

## Data Used

These notebooks use datasets from this repository:

- [regionNames/](../regionNames/) - Administrative names and identifiers
- [sdg/](../sdg/) - SDG composite indices
- [sdgVariables/](../sdgVariables/) - Granular SDG indicators (64 variables)
- [satelliteEmbeddings/](../satelliteEmbeddings/) - 64-dimensional satellite features
- [maps/](../maps/) - Province boundaries (GeoJSON)
- [datasets/](../datasets/) - Pre-merged analytical datasets

All tables are keyed by `prov_id` (3-digit INE province code, e.g. `405` = Litoral). The municipal-only id columns (`poly_id`, `asdf_id`, `mun_id`, `shapeID`, `dep_mun`) do not exist in the province tables; merge datasets on `prov_id` instead.

Data can be loaded from local relative paths under the repo root (e.g. `sdg/sdg.csv`) or directly from raw-GitHub URLs (e.g. `https://raw.githubusercontent.com/quarcs-lab/bolivia112/main/sdg/sdg.csv`), so no manual download is required.

**Example: load and merge province data**

```python
import pandas as pd

base = "https://raw.githubusercontent.com/quarcs-lab/bolivia112/main"

df_sdg = pd.read_csv(f"{base}/sdg/sdg.csv")                               # prov_id, imds, index_sdg1..17
df_sat = pd.read_csv(f"{base}/satelliteEmbeddings/satelliteEmbeddings2017.csv")  # prov_id, A00..A63

# Merge on the province key
df = pd.merge(df_sdg, df_sat, on="prov_id", how="inner")

# Verify the row count matches the 112 provinces
assert len(df) == 112
```

## Key Variables

All tables share the province key `prov_id` (3-digit INE code). Selected schemas:

- `regionNames/regionNames.csv`: `prov_id`, `prov`, `capital`, `dep`, `dep_id`, `dep_prov`, `n_mun`, `gadm_name`, `sources`
- `sdg/sdg.csv`: `prov_id`, `imds`, `index_sdg1`..`index_sdg17`
- `satelliteEmbeddings/satelliteEmbeddings2017.csv`: `prov_id`, `A00`..`A63`
- `datasets/sdgs_satelliteEmbeddings2017.csv`: `prov_id`, `prov`, `dep`, `dep_id`, `dep_prov`, `imds`, `index_sdg1`..`17`, `A00`..`A63`

### Poverty Indicators
- `index_sdg1` - Composite SDG 1 Index (No Poverty)
- `sdg1_1_eepr` - **Extreme energy poverty rate** (% of houses, 2016) ⭐
- `sdg1_1_ubn` - Unsatisfied basic needs (%)
- `sdg1_2_mpi` - Multidimensional poverty index

### Energy Indicators
- `index_sdg7` - Composite SDG 7 Index (Affordable Energy)
- `sdg7_1_ec` - Electricity coverage (% of population)
- `sdg7_1_rec` - Residential electricity consumption per capita
- `sdg7_1_cce` - Clean cooking energy (% of households)

### Satellite Features
- `A00` to `A63` - 64-dimensional embeddings from Google Earth Engine
- Derived from daytime satellite imagery at 10m resolution
- Population-weighted aggregation from municipal to province boundaries

## References

For methodological background, see:

- [Anselin, L. (2020). ESDA with PySAL](https://geodacenter.github.io/documentation.html)
- [Rey, S., Arribas-Bel, D., & Wolf, L. J. (2020). Geographic Data Science with Python](https://geographicdata.science/book/intro.html)
- [Mendez, C., & Gonzales, E. (2021). Human Capital Constraints, Spatial Dependence, and Regionalization in Bolivia](https://doi.org/10.18800/economia.202101.007)
- [Andersen, L. E., Canelas, S., Gonzales, A., Peñaranda, L. (2020). Atlas municipal de los Objetivos de Desarrollo Sostenible en Bolivia 2020](https://atlas.sdsnbolivia.org)

## Citation

If you use these notebooks in your research, please cite:

```
Mendez, C., Gonzales, E., Leoni, P., Andersen, L., Peralta, H. (2026).
bolivia112: A Province-Level Data Science Repository to Study GeoSpatial Development in Bolivia
[Data set]. GitHub. https://github.com/quarcs-lab/bolivia112
```
