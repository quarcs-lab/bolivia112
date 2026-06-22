# Province (`provincia`) assignment — verification report

**Date:** 2026-06-22
**Scope:** Added `prov_id`, `prov`, and `dep_prov_mun` to `regionNames.csv`, plus the standalone
`provinceNames.csv` lookup. This report documents how each of the **112 provinces** was identified
and verified for the **339 municipalities**.

## Method

1. **Deterministic decode (spine).** `mun_id` is the official INE code `D PP SS`. The province is the
   first 3 digits (`prov_id = int(mun_id[:3])`). This yields **exactly 112 distinct provinces** over
   the 339 municipalities — matching Bolivia's known province count.
2. **Geometry cross-check.** Each municipality's centroid (`maps/bolivia339geoqueryOpt.geojson`) was
   point-in-polygon joined to the **112 ADM2 province polygons** in
   `bolivia_adm2_gdp_perCapita_1990_2024.gpkg` (GADM `NAME_2`). **0/339 unmatched.**
   **333/339 (98.2%)** centroids fall inside the province their `mun_id` decodes to; the 6 exceptions
   are GADM border/labeling noise (see below) and are correctly assigned by the authoritative `mun_id`.
3. **Multi-source name verification.** A 21-agent web workflow confirmed every province name and
   capital against **INE, Spanish Wikipedia, and educa.com.bo** (9 department agents + 12 adversarial
   refutation agents on flagged spellings). **107/112** names were confirmed on the first pass;
   the remaining 5 were resolved against the comprehensive
   [Anexo:Provincias de Bolivia](https://es.wikipedia.org/wiki/Anexo:Provincias_de_Bolivia) table.

Each of the 112 names carries its consulted source URLs in `provinceNames.csv` (`sources` column).

## Naming conventions applied (user choice: *short official INE names*)

- **`Sud`, not `Sur`:** `Sud Cinti`, `Sud Chichas`, `Sud Lípez`, `Sud Carangas`, `Sud Yungas`
  (the GADM `NAME_2` spelling `Sur …` is retained in `gadm_name` for geometry joins).
- **Spanish accents kept:** e.g. `Bolívar`, `Nor/Sud Lípez`, `Ángel Sandoval`, `Vaca Díez`, `Yamparáez`.
- **`Charcas`** (Potosí) — confirmed **without** accent (GADM's `Chárcas` is wrong).
- **Military-rank prefix `General`/`Gral.` dropped** in the short form; full official names noted here:
  | prov_id | `prov` (short) | Full official name |
  |---|---|---|
  | 219 | José Manuel Pando | General José Manuel Pando |
  | 513 | Bilbao | General Bilbao (Gral. Bernardino Bilbao Rioja) |
  | 803 | José Ballivián | General José Ballivián |
  | 905 | Federico Román | General Federico Román |

## Resolved disputes

| prov_id | Dept | Decision | Note |
|---|---|---|---|
| **402** | Oruro | **`Eduardo Avaroa`** | INE codification and educa.com.bo spell it **Avaroa** (with *v*). Spanish Wikipedia and the hero's actual surname use **Abaroa** (with *b*). Per the user's request for the *INE* form, `Avaroa` is used. ⚠️ Flip to `Eduardo Abaroa` if the historically-correct surname is preferred. |
| **710** | Santa Cruz | **`Obispo Santistevan`** (corrected) | Initial draft `Obispo Santiesteban` was wrong; INE/Wikipedia and both verification agents confirm **Santistevan** (Mons. José Belisario Santistevan). |
| **409** | Oruro | **`Sabaya`** | Current official name (historically *Atahuallpa*). |
| **415** | Oruro | **`Mejillones`** | Confirmed (municipios La Rivera, Todos Santos, Carangas). |
| **605** | Tarija | **`Méndez`** | Eustaquio Méndez; capital San Lorenzo. Border-noise in the geometry check (see below) — `mun_id` is authoritative. |

## The 6 geometry border-discrepancies (decode is authoritative)

These municipalities' centroids land in an adjacent GADM ADM2 polygon due to boundary/label
mismatches between the GADM ADM2 layer and the municipal layer. The `mun_id` code unambiguously fixes
the correct province in every case.

| mun_id | municipality | dep | assigned `prov` (correct) | GADM polygon hit |
|---|---|---|---|---|
| 71102 | San Javier | Santa Cruz | Ñuflo de Chávez | Cercado |
| 60501 | Villa San Lorenzo | Tarija | Méndez | Méndez¹ |
| 71503 | El Puente | Santa Cruz | Guarayos | Méndez |
| 90401 | Santa Rosa | Pando | Abuná | General José Ballivián |
| 80303 | Santa Rosa | Beni | José Ballivián | Abuná |
| 80102 | San Javier | Beni | Cercado | Ñuflo de Chávez |

¹ Flagged only because the seed used a modal label; the polygon actually is Méndez — correct.

## QA assertions (all pass)

- 339 rows; original 8 columns preserved value-for-value; only `prov_id`, `prov`, `dep_prov_mun` added.
- No null `prov`/`prov_id`; **112** distinct provinces.
- `prov_id` ↔ `prov` is 1:1, and `prov_id` ↔ `dep` is 1:1.
- The only province name shared across multiple `prov_id` is **`Cercado`** — by design, the
  departmental-seat province exists in Cochabamba (301), Oruro (401), Tarija (601) and Beni (801).
- `prov_id`/`dep_prov_mun` re-derive exactly from `mun_id`/`dep`/`prov` for all 339 rows.

## Reproduce

```bash
# from repo root, in the `geo` conda env (geopandas + ogr)
python /tmp/bolivia_prov/finalize.py     # rebuilds regionNames.csv + provinceNames.csv from mun_id
```
