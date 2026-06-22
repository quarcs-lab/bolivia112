![](https://github.com/quarcs-lab/bolivia112/blob/main/images/cover2.jpg?raw=true)

# bolivia112: A Province-Level Data Science Repository to Study Regional Development in Bolivia

**bolivia112** is the **province-level** (112 provinces) replication of
[**DS4Bolivia**](../ds4bolivia/) (339 municipalities). Every municipal dataset has been aggregated to
Bolivia's **112 provinces** using **population-weighted aggregation**. The folder structure, filenames
and column schemas mirror `ds4bolivia`; the primary join key is **`prov_id`** (the first 3 digits of the
INE `mun_id`).

> 📊 **How the data was built:** see [`province_aggregation_report.md`](province_aggregation_report.md).
> Intensive variables (indices, rates, per-capita, embeddings) are population-weighted means; extensive
> variables (population, CO₂, land-cover/area counts) are summed. SDG variables are weighted by the
> Municipal Atlas `population_2020`; all other variables by the year-matched `pop/pop.csv` series.
> Everything is reproducible via [`code/build_bolivia112.py`](code/build_bolivia112.py).

This repository is organized for researchers and data scientists interested in:

* **Spatial Econometrics:** Understanding regional disparities, growth, and clustering.
* **Spatial Machine Learning:** Utilizing satellite imagery (Earth Observation) for predictive modeling.
* **Sustainable Development:** Tracking SDG indicators at the province level.

---

## 🖥️ Interactive Apps

* [Space-time dynamics of population, luminosity, land cover and GDP](apps/): Google Earth Engine
  GeoExplorer, adapted to province boundaries. *(Requires a province boundary asset in your Earth
  Engine account — see [apps/README.md](apps/README.md).)*

---

## 🐍 Computational Notebooks

Province-level adaptations of the DS4Bolivia tutorials (`GeoPandas`, `PySAL`, `scikit-learn`). Each
notebook now groups by **province** (`ADM2 = 'prov'`) over the 112 provinces.

* **EDA** — descriptive statistics, regional comparisons, NTL vs development.
* **ESDA** — spatial clusters and outliers via Global/Local Moran's I.
* **Spatial Distribution & Dependence** — classification schemes, spatial weights, LISA clusters.
* **Spatial Inequality** — Theil/Gini decomposition by department.
* **Spatial Heterogeneity (GWR & MGWR)** — spatially varying NTL↔development relationships.
* **Extended EDA + Spatial Analysis** — combined traditional + spatial methods.

See [notebooks/README.md](notebooks/README.md). Sources are kept as Jupytext `.md`; regenerate
executable notebooks with `uv run jupytext --to ipynb --execute notebooks/<name>.md`.

---

## 💾 Spatially-Explicit Datasets

All province datasets use **`prov_id`** as the primary join key.

### Core Datasets

| Dataset | Description | Documentation |
| :--- | :--- | :--- |
| **[regionNames](regionNames/)** | Administrative metadata for 112 provinces (name, capital, department, n_mun) | [README](regionNames/README.md) |
| **[sdg](sdg/)** | Aggregated SDG indices (population-weighted) | [README](sdg/README.md) |
| **[sdgVariables](sdgVariables/)** | 64 granular SDG indicators (population-weighted) | [README](sdgVariables/README.md) |
| **[pop](pop/)** | Population time series 2001-2020 (summed) | [README](pop/README.md) |
| **[ntl](ntl/)** | Night-time lights, ln per capita 2012-2020 (population-weighted) | [README](ntl/README.md) |
| **[satelliteEmbeddings](satelliteEmbeddings/)** | 64-dim embeddings, 2017 (population-weighted) | [README](satelliteEmbeddings/README.md) |
| **[datasets](datasets/)** | Pre-merged SDGs + Satellite Embeddings | [README](datasets/README.md) |
| **[gdp](gdp/)** | Province GDP per capita 1990-2024 (GADM ADM2) | [README](gdp/README.md) |

### Spatial Data

| Resource | Description |
| :--- | :--- |
| **[maps](maps/)** | 112 province boundaries (GeoJSON), from the GADM ADM2 GeoPackage |

### Code & Applications

| Resource | Description | Documentation |
| :--- | :--- | :--- |
| **[code](code/)** | `build_bolivia112.py` (reproducible aggregation) + `aggregation_rules.csv` + adapted ML models | [README](code/README.md) |
| **[notebooks](notebooks/)** | Province-level ESDA / spatial analysis tutorials | [README](notebooks/README.md) |
| **[apps](apps/)** | Interactive GeoExplorer (province) | [README](apps/README.md) |

### Master files

| File | Description |
| :--- | :--- |
| `bolivia112_v20260622.csv` | All 342 aggregated variables in one wide table (112 × 347) |
| `definitions_bolivia112_v20260622.csv` | Variable dictionary |

---

## 📜 Citation

### APA Format
Mendez, C., Gonzales, E., Leoni, P., Andersen, L., Peralta, H. (2026). bolivia112: A Province-Level Data Science Repository to Study Regional Development in Bolivia [Data set]. GitHub. https://github.com/quarcs-lab/bolivia112

### BibTeX Format

```bibtex
@misc{bolivia112_2026,
  author = {Mendez, Carlos and Gonzales, Erick and Leoni, Pedro and Andersen, Lykke and Peralta, Hendrix},
  title = {{bolivia112}: A Province-Level Data Science Repository to Study Regional Development in Bolivia},
  year = {2026},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/quarcs-lab/bolivia112}}
}
```

---

## 🚀 Getting Started

### Local Development Setup

This project uses [UV](https://docs.astral.sh/uv/) for Python package management.

```bash
git clone https://github.com/quarcs-lab/bolivia112.git
cd bolivia112
uv sync
uv run jupyter notebook            # run notebooks
uv run python code/build_bolivia112.py   # rebuild all province data from ds4bolivia
```

### Construct Your Own Dataset

All modules link by the unique province identifier **`prov_id`**.

| Dataset Category | File Path | Join Key |
| :--- | :--- | :--- |
| **Region Names** | `regionNames/regionNames.csv` | `prov_id` |
| **Socio-Economic** | `sdg/sdg.csv` | `prov_id` |
| **Detailed SDG** | `sdgVariables/sdgVariables.csv` | `prov_id` |
| **Population** | `pop/pop.csv` | `prov_id` |
| **Night-time Lights** | `ntl/ln_NTLpc.csv` | `prov_id` |
| **Satellite Features** | `satelliteEmbeddings/satelliteEmbeddings2017.csv` | `prov_id` |
| **Spatial Vector** | `maps/bolivia112provincesOpt.geojson` | `prov_id` |
| **Pre-merged** | `datasets/sdgs_satelliteEmbeddings2017.csv` | `prov_id` |

> **⚠️ Identifier note:** the primary key for joining all province datasets is **`prov_id`** (3-digit
> INE province code, e.g. `405` = Litoral). Treat it as an `int` consistently across dataframes before merging.

### Example: Integrating Attribute + Spatial Data

```python
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

BASE = "bolivia112"   # local path, or a raw GitHub URL once published

df_names = pd.read_csv(f"{BASE}/regionNames/regionNames.csv")
df_sdg   = pd.read_csv(f"{BASE}/sdg/sdg.csv")
df_emb   = pd.read_csv(f"{BASE}/satelliteEmbeddings/satelliteEmbeddings2017.csv")

df = df_names.merge(df_sdg, on="prov_id").merge(df_emb, on="prov_id")
print(f"{len(df)} provinces, {len(df.columns)} columns")

gdf = gpd.read_file(f"{BASE}/maps/bolivia112provincesOpt.geojson")
gdf["prov_id"] = gdf["prov_id"].astype(int)
gdf = gdf.merge(df, on="prov_id", how="inner")

fig, ax = plt.subplots(figsize=(12, 10))
gdf.plot(column="index_sdg1", cmap="viridis", linewidth=0.1, edgecolor="white",
         legend=True, legend_kwds={"label": "SDG 1 Index (No Poverty)", "orientation": "horizontal"}, ax=ax)
ax.set_title("Bolivia: SDG 1 Index by Province (112 provinces)", fontsize=15)
ax.set_axis_off()
plt.show()
```

---

## 🤝 Contributing

Find an error? Have a suggestion? Submit an [issue](https://github.com/quarcs-lab/bolivia112/issues)
or join the [discussion](https://github.com/quarcs-lab/bolivia112/discussions) via GitHub.
