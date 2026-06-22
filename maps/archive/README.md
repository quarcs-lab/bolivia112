# maps/archive

Placeholder for **archived / superseded province boundary versions**.

The current, canonical province boundaries live in [`../`](../):

- `bolivia112provincesOpt.geojson` — optimized (simplified) 112-province polygons.
- `bolivia112provincesFull.geojson` — full-resolution 112-province polygons.
- `bolivia_adm2_gdp_perCapita_1990_2024.gpkg` — the GADM ADM2 source GeoPackage.

When a boundary file is regenerated or replaced, move the previous version here
(with a dated filename, e.g. `bolivia112provincesOpt_v20260622.geojson`) so the
active `maps/` directory always contains only the current boundaries.

This mirrors the `maps/archive/` convention used in the sibling
[`ds4bolivia`](https://github.com/quarcs-lab/ds4bolivia) repository.
