# bolivia112 — province aggregation report

**Date:** 2026-06-22 · **Source:** `ds4bolivia/` (339 municipalities) → **the repo root** (112 provinces)

`bolivia112` is the province-level replication of `ds4bolivia`. Every municipal dataset was
aggregated to Bolivia's **112 provinces** using **population-weighted aggregation**, keyed by
**`prov_id`** (the first 3 digits of the INE `mun_id`). The folder structure, filenames and column
schemas mirror `ds4bolivia`; `asdf_id`/`mun`-level identifiers are replaced by `prov_id`/`prov`.

## Aggregation method

For each province (group of municipalities `i`):

| Variable kind | Rule |
|---|---|
| Intensive — indices, rates, %, per-capita, embeddings, climate, elevation | **population-weighted mean** `Σ(xᵢ·wᵢ) / Σ(wᵢ)` |
| Extensive — population, CO₂ totals, pixel/area counts, land-cover | **sum** |
| `.min` / `.max` companions of physical variables | **min / max** |
| `rank_imds` | **recomputed** as the rank of province `imds` (1–112) |

**Weights**
- **SDG-related variables** are weighted by **`population_2020`** (the Municipal Atlas of Sustainable
  Development population, from `sdgVariables.csv`).
- **All other variables** are weighted by **`pop/pop.csv`**, **year-matched** — `pop2015` weights any
  2015 value, etc.; non-temporal "other" variables (e.g. 2017 satellite embeddings) use `pop2017`.
- **NTL** (`ln_NTLpc`, `ln_t400NTLpc`) is the **population-weighted mean of the ln values directly**
  (year-matched weights), per project choice.
- **Missing values:** weighted means skip NaN cells and renormalize the weights over the
  municipalities that have data, so a province is never dragged to NaN by a single missing cell.

## Province geometry

`maps/bolivia112provinces{Full,Opt}.geojson` (112 features) come from the **GADM ADM2 GeoPackage**
(`bolivia_adm2_gdp_perCapita_1990_2024.gpkg`). Each polygon is matched to its `prov_id` via the unique
`(dep_id, province-name)` pair (GADM `NAME_2` resolved against `provinceNames.gadm_name`, with the
short INE `prov` name as fallback). Properties: `prov_id, prov, dep, dep_id, shapeName, COORD_X, COORD_Y`.
`gdp/gdp_perCapita_1990_2024.csv` carries the gpkg's province GDP-per-capita 1990–2024 (already
province-level — attached, not aggregated).

## Master dataset classification

`bolivia112_v20260622.csv` (112 × 347) aggregates the 350-variable master. Each variable's rule lives
in the reviewable, reproducible table **`code/aggregation_rules.csv`**. Distribution:

| rule | n | examples |
|---|---|---|
| weighted mean | 139 | all `sdg*`/`index_sdg*`/`imds`/`urbano` (weight `population_2020`); `ln_NTLpc*`; climate/precip/elev/slope/distance/malaria/photovoltaic `.mean`; MODIS agriculture/urban *ratios* |
| sum | 138 | `pop20YY`, `population_2020`, CO₂ totals (`co*`, `tr400_co*`), `ghsl` (population pixel-sum), `gisa` (impervious area), `esaLandCover_*`, `modis_landcover_*`/`modis_total_area`, `drugCult_*` |
| min / max | 32 / 32 | `.min` / `.max` of every physical variable |
| id | 8 | municipal IDs → replaced by `prov_id, prov, dep, dep_id, dep_prov` |
| recompute | 1 | `rank_imds` |

**Judgment calls (approved):** all SDG variables stay population-weighted means — including the two
count-type SDG indicators `sdg9_1_routes` and `sdg9_c_drb` — for consistency with the SDG index
methodology. CO₂, impervious area, GHSL and land-cover pixel counts are summed as extensive totals.

## Verification (all pass)

- **Counts:** every `bolivia112/*` table has exactly **112 rows**, unique `prov_id`; maps have 112
  bijective features.
- **Conservation:** Σ municipal `pop2020` = province total = **11,877,664**; Σ municipal Atlas
  `population_2020` = **11,633,371** — both preserved exactly. (The two populations differ by source,
  by design.)
- **Bounds:** every weighted-mean province value lies within the `[min, max]` of its municipalities
  (checked on `imds`).
- **Spot-checks:** Murillo `201` (La Paz; El Alto + La Paz dominate the weights) `imds`=72.7 vs Litoral
  `405` (rural Oruro) `imds`=50.1; Oropeza/Sucre `rank_imds`=4, Azurduy=111.
- **Idempotent:** re-running the builder reproduces identical outputs.

## Reproduce

```bash
uv run python code/build_bolivia112.py
```
Rebuilds every province table, the maps and the master from `ds4bolivia/` + `code/aggregation_rules.csv`.
Editing `aggregation_rules.csv` and re-running regenerates the master under the new rules.

## Caveats / handoffs

- GADM ADM2 boundaries differ slightly from the dissolved municipal boundaries at ~6 borders; data is
  grouped by `prov_id` (authoritative INE code), geometry is GADM (project choice).
- Two population series are used deliberately: `population_2020` (Atlas) for SDGs, `pop/pop.csv`
  (time series) for everything else.
- The Earth Engine app (`apps/`) and the GEE satellite-embedding re-aggregation need a province
  boundary asset uploaded to your Earth Engine account to run live.
