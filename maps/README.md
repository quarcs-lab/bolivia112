# Maps — Province Boundaries (112 provinces)

GeoJSON boundaries for Bolivia's **112 provinces**, derived from the GADM ADM2 GeoPackage
(`bolivia_adm2_gdp_perCapita_1990_2024.gpkg`). Each polygon is matched to its `prov_id` via the
unique `(dep_id, province-name)` pair. See [`../province_aggregation_report.md`](../province_aggregation_report.md).

| File | Description |
|------|-------------|
| `bolivia112provincesFull.geojson` | Full-resolution province polygons (112 features) |
| `bolivia112provincesOpt.geojson`  | Simplified polygons for fast web rendering |

**Feature properties:** `prov_id` (primary key), `prov` (province name), `dep`, `dep_id`,
`shapeName` (= `prov`), `COORD_X`, `COORD_Y` (centroid lon/lat).

```python
import geopandas as gpd
gdf = gpd.read_file("maps/bolivia112provincesOpt.geojson")
gdf["prov_id"] = gdf["prov_id"].astype(int)   # join key to any province CSV
```
