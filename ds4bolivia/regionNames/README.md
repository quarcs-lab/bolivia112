# Region Names

## Overview

This directory contains administrative metadata and identifiers for Bolivia's 339 municipalities. This dataset serves as the foundation for joining all other datasets in the repository.

Bolivia's administrative hierarchy has three levels: **Department → Province (provincia) → Municipality (municipio)**. There are **9 departments**, **112 provinces**, and **339 municipalities**.

## Files

### regionNames.csv

Official names and identifiers for all 339 municipalities, their parent **province**, and their parent **department**.

### provinceNames.csv

Standalone lookup of Bolivia's **112 provinces** (one row per province): province code, short INE name, capital, department, municipality count, the GADM `NAME_2` spelling (for joining to ADM2 geometry such as `bolivia_adm2_gdp_perCapita_1990_2024.gpkg`), and the verification sources consulted.

## Variable Dictionary

### regionNames.csv

| Variable Name | Description |
|---------------|-------------|
| **poly_id** | Polygon ID: Sequential identifier for each polygon feature |
| **asdf_id** | ASDF ID: **Primary join key** — unique spatial identifier used across all datasets in this repository |
| **mun** | Municipality name (Spanish) |
| **mun_id** | Official 5-digit INE municipality code (see *Decoding `mun_id`* below) |
| **dep** | Department name — Bolivia has 9 departments |
| **dep_id** | Department ID code (alphabetical: Beni=1 … Tarija=9) |
| **prov_id** | Province code: first 3 digits of `mun_id`, Bolivia-wide unique (e.g. `405` = Oruro / Litoral) |
| **prov** | Province name (short official INE form, Spanish accents) |
| **dep_mun** | Combined `department-municipality` label |
| **dep_prov_mun** | Combined `department-province-municipality` label |
| **shapeID** | Municipality Geoquery polygon ID: external reference for spatial matching |

### provinceNames.csv

| Variable Name | Description |
|---------------|-------------|
| **prov_id** | Province code (first 3 digits of `mun_id`) |
| **prov** | Province name (short official INE form) |
| **capital** | Province capital town |
| **dep** / **dep_id** | Parent department and its (alphabetical) ID |
| **n_mun** | Number of municipalities in the province |
| **gadm_name** | Province name as spelled in GADM / the ADM2 GeoPackage (`NAME_2`) |
| **sources** | URLs consulted to verify the name/capital |

## Decoding `mun_id`

`mun_id` is the official INE code structured as **`D PP SS`** (5 digits):

| Part | Digits | Meaning | Example (`40505`) |
|------|--------|---------|-------------------|
| `D`  | 1 | Department, **INE order** (1=Chuquisaca, 2=La Paz, 3=Cochabamba, 4=Oruro, 5=Potosí, 6=Tarija, 7=Santa Cruz, 8=Beni, 9=Pando) | `4` = Oruro |
| `PP` | 2-3 | Province within the department | `05` = Litoral |
| `SS` | 4-5 | Municipal section (municipality) | `05` = Esmeralda |

Therefore `prov_id = int(mun_id[:3])`.

> **Note:** `prov_id`'s leading digit is the **INE** department code, which differs from the
> `dep_id` column (alphabetical). For example Oruro is `4` inside `mun_id`/`prov_id` but `dep_id = 5`.

## Usage

```python
import pandas as pd

df_names = pd.read_csv("regionNames/regionNames.csv")

# All municipalities of a given province
larecaja = df_names[df_names['prov'] == 'Larecaja']

# Aggregate any indicator to the province level
prov_summary = df_merged.groupby(['dep', 'prov']).mean(numeric_only=True)

# Province lookup / join to ADM2 geometry via gadm_name
prov = pd.read_csv("regionNames/provinceNames.csv")
```

## Key Notes

- There are **339 municipalities**, **112 provinces**, and **9 departments**.
- **asdf_id** is the primary key for all joins in this repository.
- `prov`/`prov_id` were derived deterministically from `mun_id` and cross-validated against the
  ADM2 province polygons, INE, and Wikipedia — see `province_verification_report.md`.
- Province names use the short official INE form (e.g. `Murillo`, not `Pedro Domingo Murillo`;
  `Sud Cinti`, not `Sur Cinti`). The military-rank prefix `General`/`Gral.` is dropped in `prov`
  (the full form is noted in the verification report).
