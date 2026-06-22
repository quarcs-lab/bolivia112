# Statistical audit — SDG aggregation from municipalities to provinces

**Scope:** `sdg/sdg.csv` (15 indices + `imds`) and `sdgVariables/sdgVariables.csv` (62 indicators),
aggregated from 339 municipalities to 112 provinces by `code/build_bolivia112.py`.
**Method:** numerical reproduction of the engine, a semantic catalogue of every indicator's
statistical type and reference population, and an empirical **weight-sensitivity analysis**
(`code/audit_sdg_aggregation.py` → `code/sdg_aggregation_sensitivity.csv`).
**Companion data:** [`sdgVariables/sdg_reference_populations.csv`](sdgVariables/sdg_reference_populations.csv)
(per-indicator reference population + `weight_is_approximate` flag).

The aggregation **engine is numerically correct** — every weighted mean reproduces to ~1e-13 and lies
within its municipalities' [min, max]. The problems below are **statistical and conceptual**, not
bugs. A hard constraint governs the remedy: **the SDG source stores only finished rates/indices — no
numerators or denominators** — so most weight mismatches cannot be corrected exactly in-repo and are
**quantified and caveated** rather than silently "fixed". Per the agreed *moderate* appetite, only the
one family the source genuinely supports a better rule for (areal rates) was re-aggregated.

## Findings at a glance

| # | Problem | Type | Severity | Disposition |
|---|---|---|---|---|
| 1 | Weight–denominator mismatch (36/62 indicators) | Conceptual | High | **Caveat + metadata + sensitivity** (unfixable in-repo) |
| 2 | Areal rates weighted by population | Conceptual | High | **FIXED** (area-weighted) |
| 3 | Composite indices averaged, not recomputed | Conceptual | Medium | Caveat |
| 4 | `sdg9_1_routes` count averaged | Conceptual | Low | Flag/recommend |
| 5 | Imputation fabricates data | Statistical | Medium | Quantified + caveat |
| 6 | Partial municipal support | Technical | Medium | Caveat + expose support |
| 7 | MAUP / ecological inference / no uncertainty / 15 single-municipality provinces | Structural | Medium | Caveat |
| 8 | 2012–2019 indicators weighted by 2020 population | Conceptual | Low | Caveat |

---

## 1. Weight–denominator mismatch (HIGH, conceptual, mostly unfixable in-repo)

**Problem.** Every intensive SDG indicator is population-weighted by total `pop2020`. But **36 of 62
indicators are rates whose true denominator is *not* total population** — households (`sdg1_4_abs`,
`sdg11_1_hocr`, `sdg7_1_cce`, …), children <5 (`sdg2_2_cmc`, `sdg16_9_cr`), women of reproductive age
(`sdg2_2_oww`, `sdg3_7_afr`), live births (`sdg3_2_imr`, `sdg3_2_mrc`), enrolled pupils / teachers
(`sdg4_1_*`, `sdg4_c_*`), labour-force cohorts (`sdg8_5_*`, `sdg8_6_*`), electric meters
(`sdg8_4_rem`), wastewater volume (`sdg6_3_wwt`), agricultural units (`sdg2_4_*`), municipal revenue /
budget (`sdg17_1_pmtax`, `sdg16_6_pbec`), and school-age population (`sdg9_5_cd`). See the full list in
the companion metadata file (`weight_is_approximate = True`).

**Mechanism.** The correct provincial rate is `Σ(rateᵢ · denomᵢ) / Σ(denomᵢ)` over the indicator's own
reference population `denomᵢ`. Using `pop2020` instead is unbiased only if the cohort share
(children, households, …) is constant across municipalities, or uncorrelated with the rate. Where a
high-fertility, low-income municipality has both a larger child share **and** a higher malnutrition
rate, population-weighting under-weights it and biases the province value.

**Evidence (bounding the impact).** The source lacks the true denominators, so the exact bias is
unrecoverable. As a lower bound on "how much the weight choice matters," we recomputed every indicator
under population- vs. equal-weighting. The province values are **highly sensitive**: e.g.
`sdg6_1_dwc` (drinking-water coverage) moves up to **32.9 percentage points** (53 % of its
cross-province range) between the two schemes; `sdg16_6_pbec` re-ranks **80 of 112** provinces by ≥5
positions; `sdg4_c_qti`, `sdg7_1_ec`, `sdg6_2_sc`, `sdg9_5_cd` all exceed 30 % relative shifts. The
true reference-population weight is a *third* scheme distinct from both, so these numbers establish
that the choice is consequential, not that population-weighting is the worst option.

**Disposition — caveat + metadata + sensitivity (cannot fix exactly).**
- Added [`sdgVariables/sdg_reference_populations.csv`](sdgVariables/sdg_reference_populations.csv):
  every indicator's `statistical_type`, `reference_population`, `weight_used`, and a boolean
  `weight_is_approximate`. This makes the limitation machine-readable.
- Added `code/sdg_aggregation_sensitivity.csv`: per-indicator robustness, so a user can see *which*
  approximate-weight indicators are also empirically sensitive (those are the ones to treat with care).
- **Not re-weighted** — doing so would require fabricating cohort denominators (assumptions the source
  does not support). Recommended remedy if precision is needed: source municipal household/cohort
  counts (e.g. INE census tables) and re-aggregate `Σ(rate·denom)/Σ(denom)`.

## 2. Areal rates weighted by population (HIGH, conceptual) — **FIXED**

**Problem.** `sdg15_1_pa` (protected areas, % of land area), `sdg13_2_dra` (deforestation, % of
forest area) and `sdg15_5_blr` (biodiversity loss) are **areal** shares, yet were population-weighted.
Protected/deforested land sits disproportionately in sparsely-populated municipalities, so
population-weighting systematically understates them.

**Evidence.** Population and land area are **essentially uncorrelated across municipalities**
(Pearson **−0.02**, Spearman 0.27), so the weight choice is not cosmetic. Switching `sdg15_1_pa` to
land-area weighting changes province values by up to **21.7 percentage points** (e.g. Andrés Ibáñez
2.2 % → 8.0 % protected); `sdg13_2_dra` up to 2.5 pts, `sdg15_5_blr` up to 0.35 pts.

**Disposition — FIXED.** A land-area weight (`modis_total_area` pixel count, ∝ land area) was added in
`load_weights()`, and these three indicators routed to it in `build_curated()` / `classify()`. For
`sdg15_1_pa` this is **exact** (`Σ(protected)/Σ(land) = Σ(rate·area)/Σ(area)`, verified to 7e-15). For
the two **forest**-area rates, total land area is an **improved proxy** for forest area (flagged as
approximate in the metadata; forest-pixel weighting would be exact but needs the land-cover layer).
*Caveat introduced:* the province `index_sdg13`/`index_sdg15` are still pop-weighted means of the
municipal indices, so they are no longer perfectly consistent with the re-weighted indicators (see #3).

## 3. Composite indices averaged, not recomputed (MEDIUM, conceptual)

**Problem.** `imds` and `index_sdg1…17` are population-weighted **means of municipal index values**.
The SDSN methodology builds each index by normalising indicators to [0, 100] against fixed bounds and
averaging; the statistically consistent province index would **recompute** that normalisation from the
*province* indicators. Averaging a non-linear normalisation is not equal to normalising the average
(an aggregation-consistency / ecological error).

**Disposition — caveat.** The SDSN normalisation bounds and goal weights are **not in the repo**, so a
faithful recomputation is impossible here. Documented as a known inconsistency; the province indices
should be read as "population-weighted municipal index averages," not as indices recomputed at the
province level. (Recompute upstream in `ds4bolivia` if exact province indices are required.)

## 4. `sdg9_1_routes` — extensive count aggregated as a weighted mean (LOW)

**Problem.** "Number of railways/primary roads entering/leaving the municipality" is an extensive
**count**, but is population-weight-averaged like a rate (the build labels this "SDG count-type kept as
weighted mean"). A pop-weighted average count has no clean interpretation; summing would double-count
shared corridors.

**Disposition — flag/recommend, not changed.** It feeds the SDSN `index_sdg9` construction as a
normalised score, so neither sum nor mean is unambiguously correct at province level. Flagged in the
metadata (`statistical_type = count_extensive`); recommend treating it as an ordinal connectivity proxy
only.

## 5. Imputation fabricates data (MEDIUM, statistical)

**Problem.** Where *all* a province's municipalities lack an indicator, the build fills the cell with
the department's population-weighted mean (added in earlier work). This injects **synthetic** values:
8 cells — `sdg1_1_eepr`, `sdg8_4_rem`, `sdg10_2_iec` for **904 (Abuná)** & **905 (Federico Román)**;
`sdg2_4_pual`, `sdg2_4_td` for **301 (Cercado, Cochabamba)**. Imputing toward a department centroid
**shrinks variance** and **inflates spatial autocorrelation**, biasing ESDA (Moran's I, LISA) and any
regression that doesn't account for it.

**Disposition — quantified + caveat (kept).** Only 8 of ~7 000 SDG cells are imputed and **all are
flagged** by a `<var>_imputed` column, so the footprint is small and transparent. Guidance added:
**exclude `_imputed` rows from inferential models, or include the flag as a covariate**; never treat
imputed cells as observations in spatial-dependence statistics. (The earlier choice to impute is
retained per the project owner's decision; this audit documents its statistical cost.)

## 6. Partial municipal support (MEDIUM, technical)

**Problem.** The weighted mean renormalises over municipalities that *have* data, so a province value
can rest on very few observations without any visible indicator. For the sparse indicators
(`sdg1_1_eepr`, `sdg8_4_rem`, `sdg10_2_iec`) **19–20 provinces** are backed by a *single* municipality;
median support for those columns is just 2 municipalities.

**Disposition — caveat + expose support.** The diagnostics report per-indicator `min_support` and
`median_support`. Recommendation: surface an effective-support count (municipalities behind each value)
alongside the data and down-weight low-support provinces in inference.

## 7. Structural limits — MAUP, ecological inference, no uncertainty (MEDIUM)

- **MAUP.** All province-level correlations, Moran's I and ML results are scale-dependent; they will
  differ from municipal or individual relationships. Province conclusions must not be read as
  municipal/individual effects (ecological-inference caution).
- **15 single-municipality "provinces"** (`108, 301, 311, 315, 410, 411, 413, 414, 416, 515, 516, 601,
  606, 712, 805`) are **exact copies** of one municipality — no aggregation, no within-unit
  information, and an uncertainty profile unlike multi-municipality provinces.
- **No uncertainty propagated.** Province values carry no standard error and **no within-province
  dispersion** is retained (only `min`/`max` for the physical variables, which are out of SDG scope).
  Small provinces are noisier but indistinguishable from precise ones in the data.

**Disposition — caveat.** Documented; recommend exposing `n_mun` and (cheaply) a within-province spread
for headline indicators.

## 8. Temporal weight mismatch (LOW, conceptual)

Indicators measured 2012–2019 are weighted by **2020** population shares. Population shares drift over
time, so a small inconsistency exists. Low impact (shares are highly correlated year-to-year);
documented, not changed.

---

## What this audit changed

| Change | File(s) |
|---|---|
| Area-weighting for the 3 areal rates (#2) | `code/build_bolivia112.py`; regenerated `sdgVariables/sdgVariables.csv`, master, `code/aggregation_rules.csv` |
| Reference-population metadata + approximate-weight flags (#1, #4) | `sdgVariables/sdg_reference_populations.csv` (new) |
| Reproducible weight-sensitivity diagnostics | `code/audit_sdg_aggregation.py`, `code/sdg_aggregation_sensitivity.csv` (new) |
| Caveats | `sdgVariables/README.md`, `sdg/README.md`, `province_aggregation_report.md` |

Everything else was left faithful to the SDSN/`ds4bolivia` source and **caveated** rather than altered.

## Guidance for users
1. Check `sdg_reference_populations.csv` before using an indicator: if `weight_is_approximate = True`,
   the province value is a population-weighted approximation of a non-population rate.
2. Cross-reference `sdg_aggregation_sensitivity.csv`: approximate-weight **and** weight-sensitive
   indicators (low Spearman / many rank shifts) deserve the most caution.
3. Exclude `_imputed` rows from inference, or model the flag.
4. Down-weight or annotate single-municipality and low-support provinces.
5. Treat `imds`/`index_sdg*` as averaged municipal indices, not province-recomputed indices.

## Reproduce
```bash
uv run python code/audit_sdg_aggregation.py     # diagnostics + sensitivity CSV
rm code/aggregation_rules.csv && uv run python code/build_bolivia112.py && uv run python code/build_bolivia112.py
```
