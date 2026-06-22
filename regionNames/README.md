# Region Names

## Overview

This directory contains administrative metadata and identifiers for Bolivia's 112 provinces. This dataset serves as the foundation for joining all other datasets in the repository.

Bolivia's administrative hierarchy has three levels: **Department → Province (provincia) → Municipality (municipio)**. There are **9 departments**, **112 provinces**, and **339 municipalities**. This repository works at the **province** level: the *data* folders aggregate municipal values to provinces by population weighting (intensive variables = weighted mean, extensive variables = sum — see [../province_aggregation_report.md](../province_aggregation_report.md)). The columns in **this** file are administrative **identifiers** — they are *derived*, not aggregated (see *How these identifiers were generated* below).

## Files

### regionNames.csv

Official names and identifiers for all **112 provinces** (one row per province): province code, short INE name, capital, parent department, the number of municipalities aggregated into the province, the GADM `NAME_2` spelling (for joining to ADM2 geometry such as `bolivia_adm2_gdp_perCapita_1990_2024.gpkg`), and the verification sources consulted.

## Variable Dictionary

### regionNames.csv

| Variable Name | Description |
|---------------|-------------|
| **prov_id** | Province code: **Primary join key** — official 3-digit INE code, Bolivia-wide unique, used across all datasets in this repository (e.g. `405` = Oruro / Litoral) |
| **prov** | Province name (short official INE form, Spanish accents) |
| **capital** | Province capital town |
| **dep** | Department name — Bolivia has 9 departments |
| **dep_id** | Department ID code (alphabetical: Beni=1 … Tarija=9) |
| **dep_prov** | Combined `department-province` label |
| **n_mun** | Number of municipalities aggregated into the province |
| **gadm_name** | Province name as spelled in GADM / the ADM2 GeoPackage (`NAME_2`) |
| **sources** | URLs consulted to verify the name/capital |

## How these identifiers were generated

These columns are **derived identifiers** (not aggregated municipal values), produced by
`load_crosswalk()` and `build_region_names()` in
[`../code/build_bolivia112.py`](../code/build_bolivia112.py):

- **`prov_id`** = first 3 digits of the INE municipal code, `int(mun_id[:3])`.
- **`prov`, `capital`, `gadm_name`, `sources`** come from the vendored
  [`../code/provinceNames.csv`](../code/provinceNames.csv), cross-validated against the GADM ADM2
  polygons, INE and Wikipedia (see `province_verification_report.md`).
- **`n_mun`** = number of municipalities whose `mun_id` maps to each `prov_id`.
- **`dep`, `dep_id`, `dep_prov`** = department name, alphabetical department code, and combined label.

## Decoding `prov_id`

`prov_id` is the official INE province code structured as **`D PP`** (3 digits):

| Part | Digits | Meaning | Example (`405`) |
|------|--------|---------|-----------------|
| `D`  | 1 | Department, **INE order** (1=Chuquisaca, 2=La Paz, 3=Cochabamba, 4=Oruro, 5=Potosí, 6=Tarija, 7=Santa Cruz, 8=Beni, 9=Pando) | `4` = Oruro |
| `PP` | 2-3 | Province within the department | `05` = Litoral |

`prov_id` corresponds to the first 3 digits of the underlying INE municipal code (`mun_id`), so `prov_id = int(mun_id[:3])` at the source municipal level.

> **Note:** `prov_id`'s leading digit is the **INE** department code, which differs from the
> `dep_id` column (alphabetical). For example Oruro is `4` inside `prov_id` but `dep_id = 5`.

## Usage

```python
import pandas as pd

df_names = pd.read_csv("regionNames/regionNames.csv")

# Look up a given province
larecaja = df_names[df_names['prov'] == 'Larecaja']

# Aggregate any indicator to the department level
dep_summary = df_merged.groupby(['dep']).mean(numeric_only=True)

# Join to ADM2 province geometry via gadm_name (e.g. the ADM2 GeoPackage),
# or merge other datasets on the primary key prov_id
df_merged = pd.merge(df_sdg, df_names, on='prov_id', how='inner')
```

## Key Notes

- There are **112 provinces**, **9 departments**, and **339 underlying municipalities**.
- **prov_id** is the primary key for all joins in this repository.
- Province values are **population-weighted aggregations** of the municipal data — see [../province_aggregation_report.md](../province_aggregation_report.md).
- `prov`/`prov_id` were derived deterministically from the INE municipal codes and cross-validated against the
  ADM2 province polygons, INE, and Wikipedia — see `province_verification_report.md`.
- Province names use the short official INE form (e.g. `Murillo`, not `Pedro Domingo Murillo`;
  `Sud Cinti`, not `Sur Cinti`). The military-rank prefix `General`/`Gral.` is dropped in `prov`
  (the full form is noted in the verification report).
