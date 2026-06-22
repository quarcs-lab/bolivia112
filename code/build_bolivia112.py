#!/usr/bin/env python3
"""Build bolivia112 — the province-level (112 provinces) replication of ds4bolivia.

Aggregates municipal (339) data to provinces (112) via population-weighted aggregation:
  * intensive variables (indices, rates, per-capita, embeddings) -> population-weighted mean
        prov_value = sum(x_i * w_i) / sum(w_i)   over municipalities i with non-missing x_i
  * extensive variables (population, counts/totals)             -> sum
  * min / max variables                                        -> min / max

Weights:
  * SDG-related variables  -> INE pop2020 (pop/pop.csv). The province `population_2020` column is
                              likewise set to INE pop2020 (= sum of municipal pop2020), so it is
                              consistent with pop/pop.csv (not the Municipal Atlas count).
  * areal SDG rates        -> land area (modis_total_area); sdg15_1_pa, sdg13_2_dra, sdg15_5_blr
                              measure % of land/forest area, so pop-weighting is wrong (see
                              sdg_aggregation_audit.md)
  * all other variables    -> pop/pop.csv, year-matched (pop2015 weights any 2015 value;
                              non-temporal "other" vars use pop2017)

All-NaN SDG cells (a province whose municipalities ALL lack a given SDG variable) are imputed with
the pop2020-weighted mean of the same department's provinces that have data, and marked with a
companion boolean `<var>_imputed` column.

Grouping key: prov_id (first 3 digits of mun_id), from <ds4bolivia>/regionNames/regionNames.csv.
Output: <repo-root>/<folder>/<same filename>.csv, keyed by prov_id, identical column schemas.

Layout: this repo IS the province project (outputs at the repo root). The municipal source
`ds4bolivia/` may live inside the repo or as a sibling folder next to it; the ADM2 GeoPackage may
live in `maps/` or at the repo root. Both locations are auto-detected below.

Idempotent: re-running reproduces the same outputs. Run from anywhere:
    uv run python code/build_bolivia112.py
"""
import csv
import os
import re

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
B112 = os.path.dirname(HERE)                       # repo root (province project lives at root)
REPO = B112
# municipal source: in-repo ds4bolivia/, else sibling ../ds4bolivia
DS4 = next((p for p in [os.path.join(B112, "ds4bolivia"),
                        os.path.join(os.path.dirname(B112), "ds4bolivia")]
            if os.path.isdir(p)), os.path.join(os.path.dirname(B112), "ds4bolivia"))
# ADM2 GeoPackage: prefer maps/, else repo root
_GPKG_NAME = "bolivia_adm2_gdp_perCapita_1990_2024.gpkg"
GPKG = next((p for p in [os.path.join(B112, "maps", _GPKG_NAME), os.path.join(B112, _GPKG_NAME)]
             if os.path.exists(p)), os.path.join(B112, "maps", _GPKG_NAME))
# vendored 112-province lookup (build input; makes the build independent of the ds4bolivia copy)
PROVNAMES = os.path.join(HERE, "provinceNames.csv")


def p_in(*a):
    return os.path.join(DS4, *a)


def p_out(*a):
    path = os.path.join(B112, *a)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path


def write_csv(df, *out_parts):
    df.to_csv(p_out(*out_parts), index=False, quoting=csv.QUOTE_MINIMAL)
    print(f"  wrote {os.path.join(*out_parts)}  ({len(df)} rows, {len(df.columns)} cols)")


# ---------------------------------------------------------------- Stage 0
def load_crosswalk():
    # works with the original ds4bolivia regionNames (no prov columns): derive prov_id from
    # mun_id (first 3 digits) and attach the province name from the vendored provinceNames.csv.
    rn = pd.read_csv(p_in("regionNames", "regionNames.csv"), dtype={"mun_id": str})
    rn["prov_id"] = rn["mun_id"].str.strip().str[:3].astype(int)
    pn = pd.read_csv(PROVNAMES)
    rn = rn.merge(pn[["prov_id", "prov"]], on="prov_id", how="left")
    assert rn["prov"].notna().all(), "a prov_id has no name in provinceNames.csv"
    return rn[["asdf_id", "prov_id", "prov", "dep", "dep_id"]].copy()


# Areal SDG rates: denominator is land/forest area, NOT population, so they are weighted by land
# area ("area" weight) rather than pop2020. sdg15_1_pa (% of land area) is exact; the two forest
# rates use total land area as a proxy for forest area. See sdg_aggregation_audit.md (finding 2).
AREAL_RATES = {"sdg15_1_pa", "sdg13_2_dra", "sdg15_5_blr"}


def load_weights():
    """Return dict of weight-name -> Series(asdf_id -> weight). Keys are INE pop years
    ("2001".."2020"); "2020" is the SDG weight. "area" is a land-area weight for areal SDG rates.
    (The Municipal-Atlas population is no longer used as a weight.)"""
    w = {}
    pop = pd.read_csv(p_in("pop", "pop.csv")).set_index("asdf_id")
    for c in pop.columns:                                                 # pop2001..pop2020
        m = re.search(r"(20\d\d)", c)
        if m:
            w[m.group(1)] = pop[c].astype(float)
    # land-area weight: municipal modis_total_area pixel count ∝ land area (mean over years, which
    # is ~time-invariant). Used for the areal SDG rates above. Read from the ds4bolivia master.
    master = pd.read_csv(p_in("ds4bolivia_v20250523.csv"))
    acols = [c for c in master.columns if c.startswith("modis_total_area")]
    if acols:
        w["area"] = master.set_index("asdf_id")[acols].mean(axis=1).astype(float)
    return w


# ---------------------------------------------------------------- engine
def aggregate(df, rules, weights, xwalk):
    """df keyed by asdf_id; rules = list of (col, how, weight_key).
    how in {'wmean','sum','min','max'}; weight_key indexes `weights` (wmean only)."""
    m = df.merge(xwalk[["asdf_id", "prov_id"]], on="asdf_id", how="left")
    assert m["prov_id"].notna().all(), "municipality missing prov_id"
    g = m.groupby("prov_id")
    out = pd.DataFrame(index=sorted(m["prov_id"].unique()))
    out.index.name = "prov_id"
    for col, how, wkey in rules:
        if how == "sum":
            out[col] = g[col].sum(min_count=1)
        elif how == "min":
            out[col] = g[col].min()
        elif how == "max":
            out[col] = g[col].max()
        elif how == "wmean":
            wcol = m["asdf_id"].map(weights[wkey]).astype(float)
            num = (m[col] * wcol).groupby(m["prov_id"]).sum(min_count=1)
            den = wcol.where(m[col].notna()).groupby(m["prov_id"]).sum(min_count=1)
            out[col] = num / den
        else:
            raise ValueError(how)
    return out.reset_index()


def year_of(col, default="2017"):
    m = re.search(r"(20\d\d)", col)
    return m.group(1) if m else default


def is_sdg_family(v):
    """SDG-family variable: the sdg* indicators, the index_sdg* composites, and imds."""
    return v.startswith(("sdg", "index_sdg")) or v == "imds"


def ine_pop2020_by_prov(xwalk, weights):
    """Series(prov_id -> sum of municipal INE pop2020). Used as the province population_2020."""
    s = weights["2020"]                                   # index: asdf_id
    df = pd.DataFrame({"asdf_id": s.index, "pop2020": s.values})
    df = df.merge(xwalk[["asdf_id", "prov_id"]], on="asdf_id", how="left")
    return df.groupby("prov_id")["pop2020"].sum()


def impute_sdg_dept_mean(prov_df, xwalk, weights):
    """Fill all-NaN SDG-family province cells with the pop2020-weighted mean of the same
    department's provinces that have data; append a boolean `<var>_imputed` flag per filled
    column (True only at the imputed provinces). Non-SDG columns are never touched, and partial
    coverage (some municipalities present) is left to the weighted-mean engine, so only genuine
    all-municipalities-missing cells are imputed. Returns a copy with any flag columns appended."""
    df = prov_df.copy()
    dep = xwalk.drop_duplicates("prov_id").set_index("prov_id")["dep_id"]
    popw = ine_pop2020_by_prov(xwalk, weights)            # prov_id -> pop2020
    depid = df["prov_id"].map(dep)
    flags = {}
    for col in [c for c in df.columns if c != "prov_id" and is_sdg_family(c)]:
        s = pd.to_numeric(df[col], errors="coerce")
        if not s.isna().any():
            continue
        flag = pd.Series(False, index=df.index)
        for i in df.index[s.isna()]:                     # donors use ORIGINAL data (stale s), not
            donors = (depid == depid[i]) & s.notna()     # other imputed cells in the same dept
            if not donors.any():
                continue
            w = df.loc[donors, "prov_id"].map(popw).astype(float).to_numpy()
            df.loc[i, col] = float(np.average(s[donors].to_numpy(), weights=w))
            flag[i] = True
        if flag.any():
            flags[col + "_imputed"] = flag
    for k, v in flags.items():
        df[k] = v
    return df


# ---------------------------------------------------------------- Stage 0 output
def build_region_names(xwalk):
    pn = pd.read_csv(PROVNAMES)
    pn = pn.sort_values("prov_id").reset_index(drop=True)
    pn["dep_prov"] = pn["dep"] + "-" + pn["prov"]
    cols = ["prov_id", "prov", "capital", "dep", "dep_id", "dep_prov", "n_mun", "gadm_name", "sources"]
    write_csv(pn[cols], "regionNames", "regionNames.csv")
    return pn


# ---------------------------------------------------------------- Stage 1
def build_curated(xwalk, weights):
    # sdg.csv : imds + index_sdg* -> wmean by INE pop2020
    sdg = pd.read_csv(p_in("sdg", "sdg.csv"))
    cols = [c for c in sdg.columns if c != "asdf_id"]
    prov_sdg = aggregate(sdg, [(c, "wmean", "2020") for c in cols], weights, xwalk)
    prov_sdg = impute_sdg_dept_mean(prov_sdg, xwalk, weights)  # no-op today (sdg.csv has no all-NaN)
    write_csv(prov_sdg, "sdg", "sdg.csv")

    # sdgVariables.csv : all SDG vars wmean by INE pop2020; population_2020 := INE pop2020
    sv = pd.read_csv(p_in("sdgVariables", "sdgVariables.csv"))
    rules = []
    for c in sv.columns:
        if c == "asdf_id":
            continue
        if c == "population_2020":
            rules.append((c, "sum", None))
        elif c in AREAL_RATES and "area" in weights:        # areal rate -> land-area weighted
            rules.append((c, "wmean", "area"))
        else:
            rules.append((c, "wmean", "2020"))
    prov_sv = aggregate(sv, rules, weights, xwalk)
    # population_2020 column := INE pop2020 (sum of municipal pop2020), not the Atlas sum
    ine_pop = ine_pop2020_by_prov(xwalk, weights)
    prov_sv["population_2020"] = prov_sv["prov_id"].map(ine_pop).round().astype("Int64")
    # fill all-NaN SDG cells (e.g. 904/905 Pando, 301 Cochabamba) by pop-weighted dept mean
    prov_sv = impute_sdg_dept_mean(prov_sv, xwalk, weights)
    write_csv(prov_sv, "sdgVariables", "sdgVariables.csv")

    # pop.csv : pop20YY -> sum
    pop = pd.read_csv(p_in("pop", "pop.csv"))
    cols = [c for c in pop.columns if c != "asdf_id"]
    write_csv(aggregate(pop, [(c, "sum", None) for c in cols], weights, xwalk),
              "pop", "pop.csv")

    # ntl/ln_NTLpc.csv : wmean of ln values, year-matched pop weight
    ntl = pd.read_csv(p_in("ntl", "ln_NTLpc.csv"))
    rules = [(c, "wmean", year_of(c)) for c in ntl.columns if c != "asdf_id"]
    write_csv(aggregate(ntl, rules, weights, xwalk), "ntl", "ln_NTLpc.csv")

    # satelliteEmbeddings 2017 : A00..A63 -> wmean by pop2017
    emb = pd.read_csv(p_in("satelliteEmbeddings", "satelliteEmbeddings2017.csv"))
    rules = [(c, "wmean", "2017") for c in emb.columns if c != "asdf_id"]
    write_csv(aggregate(emb, rules, weights, xwalk),
              "satelliteEmbeddings", "satelliteEmbeddings2017.csv")

    # satelliteEmbeddings 2017 pop-weighted : A* wmean by pop2017; pop_sum -> sum
    embw = pd.read_csv(p_in("satelliteEmbeddings", "satelliteEmbeddings2017popWeighted.csv"))
    rules = []
    for c in embw.columns:
        if c == "asdf_id":
            continue
        rules.append((c, "sum", None) if c == "pop_sum" else (c, "wmean", "2017"))
    write_csv(aggregate(embw, rules, weights, xwalk),
              "satelliteEmbeddings", "satelliteEmbeddings2017popWeighted.csv")


# ---------------------------------------------------------------- Stage 1: rebuild datasets/
def build_datasets(region_prov):
    sdg = pd.read_csv(p_out("sdg", "sdg.csv"))
    emb = pd.read_csv(p_out("satelliteEmbeddings", "satelliteEmbeddings2017.csv"))
    ids = region_prov[["prov_id", "prov", "dep", "dep_id", "dep_prov"]]
    merged = ids.merge(sdg, on="prov_id").merge(emb, on="prov_id")
    write_csv(merged, "datasets", "sdgs_satelliteEmbeddings2017.csv")


# ---------------------------------------------------------------- Stage 2: maps
def build_maps(xwalk):
    """Province polygons from the GADM ADM2 GeoPackage, prov_id attached by
    spatial majority vote of member municipality centroids (robust to border noise)."""
    try:
        import geopandas as gpd
    except ImportError:
        print("  maps skipped (geopandas not installed)")
        return
    gpkg = GPKG
    if not os.path.exists(gpkg):
        print("  maps skipped (ADM2 gpkg not found)")
        return
    print("Stage 2: province maps (GADM ADM2)")
    import unicodedata
    adm2 = gpd.read_file(gpkg).to_crs(4326)[["GID_2", "NAME_2", "geometry"]]

    # GADM department index (alphabetical) -> our department name
    GADM_DEP = {1: "Chuquisaca", 2: "Cochabamba", 3: "Beni", 4: "La Paz",
                5: "Oruro", 6: "Pando", 7: "Potosí", 8: "Santa Cruz", 9: "Tarija"}
    pn = pd.read_csv(PROVNAMES)
    dep2id = pn.drop_duplicates("dep").set_index("dep")["dep_id"].to_dict()
    adm2["dep_id"] = adm2["GID_2"].str.split(".").str[1].astype(int).map(GADM_DEP).map(dep2id)

    def norm(x):
        x = unicodedata.normalize("NFKD", str(x)).encode("ascii", "ignore").decode().lower()
        return x.replace("general", "").replace("gral", "").replace(".", "").replace("-", " ").strip()

    # (dep_id, name) -> prov_id, keyed on gadm_name first, prov name as fallback
    g_lut = {(r.dep_id, norm(r.gadm_name)): r.prov_id for r in pn.itertuples()}
    p_lut = {(r.dep_id, norm(r.prov)): r.prov_id for r in pn.itertuples()}
    adm2["prov_id"] = adm2.apply(
        lambda r: g_lut.get((r.dep_id, norm(r.NAME_2)))
        or p_lut.get((r.dep_id, norm(r.NAME_2))), axis=1).astype("Int64")

    assert adm2["prov_id"].notna().all(), \
        f"unmapped GADM polygons: {adm2[adm2.prov_id.isna()][['GID_2','NAME_2']].values.tolist()}"
    assert adm2["prov_id"].nunique() == 112 == len(adm2), \
        f"not bijective: {adm2['prov_id'].nunique()} prov / {len(adm2)} polys"

    g = adm2[["prov_id", "geometry"]].merge(pn[["prov_id", "prov", "dep", "dep_id"]], on="prov_id")
    rp = g.geometry.representative_point()
    g["COORD_X"], g["COORD_Y"] = rp.x.round(6), rp.y.round(6)
    g["shapeName"] = g["prov"]
    g = g[["prov_id", "prov", "dep", "dep_id", "shapeName", "COORD_X", "COORD_Y", "geometry"]]
    g = g.sort_values("prov_id").reset_index(drop=True)

    full = p_out("maps", "bolivia112provincesFull.geojson")
    g.to_file(full, driver="GeoJSON")
    opt = g.copy()
    opt["geometry"] = opt.geometry.simplify(0.005, preserve_topology=True)
    opt.to_file(p_out("maps", "bolivia112provincesOpt.geojson"), driver="GeoJSON")
    print(f"  wrote maps/bolivia112provincesFull.geojson + ...Opt.geojson "
          f"({len(g)} features, {os.path.getsize(full)//1024} KB full)")
    return g


# ---------------------------------------------------------------- Stage 3: master
ID_COLS = {"poly_id", "asdf_id", "mun", "mun_id", "dep", "dep_id", "dep_mun", "shapeID"}
SUM_PREFIXES = ("tr400_co", "ghsl", "gisa", "esaLandCover", "modis_total_area",
                "modis_landcover", "drugCult_count", "drugCult_none", "drugCult_coca")


def classify(v, label):
    """Return (agg, weight, note). agg in {id,recompute,wmean,sum,min,max}."""
    lab = (label or "").lower()
    if v in ID_COLS:
        return ("id", "", "replaced by province keys")
    if v == "rank_imds":
        return ("recompute", "", "ranking recomputed over the 112 provinces")
    if v.startswith(("sdg", "index_sdg")) or v in {"imds", "urbano_2012", "population_2020"}:
        if v == "population_2020":
            return ("sum", "", "set to INE pop2020 (= sum of municipal pop2020)")
        if v in AREAL_RATES:
            return ("wmean", "area", "areal rate: weighted by land area, not population")
        note = "SDG count-type kept as weighted mean (SDG rule)" if ("number" in lab or v.endswith("routes")) else ""
        return ("wmean", "2020", note)
    if re.fullmatch(r"pop20\d\d", v):
        return ("sum", "", "population count")
    if "NTLpc" in v:
        return ("wmean", year_of(v), "ln per-capita; weighted mean of ln values")
    if re.fullmatch(r"co20\d\d", v) or v.startswith(SUM_PREFIXES):
        return ("sum", "", "extensive count/area/total")
    if v.startswith(("modis_agriculture", "modis_urban")):
        return ("wmean", year_of(v), "ratio/fraction")
    m = re.search(r"(mean|min|max)$", v)
    if m:
        how = {"mean": "wmean", "min": "min", "max": "max"}[m.group(1)]
        return (how, year_of(v) if how == "wmean" else "", "")
    return ("wmean", year_of(v), "intensive (default)")


def generate_master_rules():
    defs = pd.read_csv(p_in("definitions_ds4bolivia_v20250523.csv"))
    defs = defs.rename(columns={defs.columns[0]: "idx"})
    rows = []
    for _, r in defs.iterrows():
        agg, weight, note = classify(r["varname"], r["varlabel"])
        rows.append({"idx": r["idx"], "varname": r["varname"], "varlabel": r["varlabel"],
                     "agg": agg, "weight": weight, "note": note})
    rules = pd.DataFrame(rows)
    write_csv(rules, "code", "aggregation_rules.csv")
    print("  rule distribution:", dict(rules["agg"].value_counts()))
    return rules


def aggregate_master(xwalk, weights, region_prov):
    # weight kept as str: weight keys are year labels ("2020", "2017", ...) that pandas would
    # otherwise read back as floats (2020.0) and fail the string-keyed `weights` lookup.
    rules = pd.read_csv(p_out("code", "aggregation_rules.csv"),
                        dtype={"weight": str}).fillna({"weight": ""})
    df = pd.read_csv(p_in("ds4bolivia_v20250523.csv"))
    agg_rules, recompute = [], []
    for _, r in rules.iterrows():
        v, how, wk = r["varname"], r["agg"], r["weight"]
        if how == "id" or v not in df.columns:
            continue
        if how == "recompute":
            recompute.append(v)
        else:
            agg_rules.append((v, how, wk if wk else "2017"))
    out = aggregate(df, agg_rules, weights, xwalk)
    prov = region_prov[["prov_id", "prov", "dep", "dep_id", "dep_prov"]].merge(out, on="prov_id")
    if "imds" in prov.columns and "rank_imds" in recompute:
        prov["rank_imds"] = prov["imds"].rank(ascending=False, method="min").astype(int)
    if "population_2020" in prov.columns:                       # := INE pop2020, like sdgVariables
        ine_pop = ine_pop2020_by_prov(xwalk, weights)
        prov["population_2020"] = prov["prov_id"].map(ine_pop).round().astype("Int64")
    for c in [c for c in prov.columns if re.fullmatch(r"pop20\d\d", c)]:
        prov[c] = prov[c].round().astype("Int64")
    # fill all-NaN SDG cells by pop-weighted dept mean (same rule as the curated sdgVariables)
    prov = impute_sdg_dept_mean(prov, xwalk, weights)
    ver = "v20260622"
    write_csv(prov, f"bolivia112_{ver}.csv")
    # definitions: drop municipal-only ID rows, add province keys + any imputation-flag columns
    defs = pd.read_csv(p_in("definitions_ds4bolivia_v20250523.csv"))
    defs = defs.rename(columns={defs.columns[0]: "idx"})
    keep = defs[~defs["varname"].isin(ID_COLS)].copy()
    keep.loc[keep["varname"] == "population_2020", "varlabel"] = \
        "Population 2020 (INE; sum of municipal pop2020 — consistent with pop/pop.csv)"
    head = pd.DataFrame({"varname": ["prov_id", "prov", "dep", "dep_id", "dep_prov"],
                         "varlabel": ["Province code (first 3 digits of mun_id)", "Province name",
                                      "Department name", "Department ID",
                                      "Department-Province label"]})
    flagcols = [c for c in prov.columns if c.endswith("_imputed")]
    tail = pd.DataFrame({"varname": flagcols,
                         "varlabel": [f"1 if {c[:-len('_imputed')]} was imputed (pop-weighted "
                                      f"department mean; all member municipalities missing)"
                                      for c in flagcols]})
    out_defs = pd.concat([head, keep[["varname", "varlabel"]], tail], ignore_index=True)
    out_defs.insert(0, "idx", range(len(out_defs)))
    write_csv(out_defs, f"definitions_bolivia112_{ver}.csv")


# ---------------------------------------------------------------- gdp from gpkg
def build_gdp():
    """Province GDP per capita 1990-2024 already exists at province level in the gpkg."""
    try:
        import geopandas as gpd
    except ImportError:
        return
    gpkg = GPKG
    if not os.path.exists(gpkg):
        return
    import unicodedata
    g = gpd.read_file(gpkg)
    pn = pd.read_csv(PROVNAMES)
    GADM_DEP = {1: "Chuquisaca", 2: "Cochabamba", 3: "Beni", 4: "La Paz",
                5: "Oruro", 6: "Pando", 7: "Potosí", 8: "Santa Cruz", 9: "Tarija"}
    dep2id = pn.drop_duplicates("dep").set_index("dep")["dep_id"].to_dict()

    def norm(x):
        x = unicodedata.normalize("NFKD", str(x)).encode("ascii", "ignore").decode().lower()
        return x.replace("general", "").replace("gral", "").replace(".", "").replace("-", " ").strip()

    g["dep_id"] = g["GID_2"].str.split(".").str[1].astype(int).map(GADM_DEP).map(dep2id)
    g_lut = {(r.dep_id, norm(r.gadm_name)): r.prov_id for r in pn.itertuples()}
    p_lut = {(r.dep_id, norm(r.prov)): r.prov_id for r in pn.itertuples()}
    g["prov_id"] = g.apply(lambda r: g_lut.get((r.dep_id, norm(r.NAME_2)))
                           or p_lut.get((r.dep_id, norm(r.NAME_2))), axis=1).astype("Int64")
    years = [c for c in g.columns if re.fullmatch(r"\d{4}", str(c))]
    out = (g[["prov_id"] + years].rename(columns={y: f"gdppc{y}" for y in years})
           .merge(pn[["prov_id", "prov", "dep", "dep_id"]], on="prov_id")
           .sort_values("prov_id"))
    out = out[["prov_id", "prov", "dep", "dep_id"] + [f"gdppc{y}" for y in years]]
    write_csv(out, "gdp", "gdp_perCapita_1990_2024.csv")


# ---------------------------------------------------------------- verification
def verify(xwalk, weights):
    print("\n== verification ==")
    pn = pd.read_csv(PROVNAMES)
    files = {
        "regionNames/regionNames.csv": "prov_id",
        "sdg/sdg.csv": "prov_id",
        "sdgVariables/sdgVariables.csv": "prov_id",
        "pop/pop.csv": "prov_id",
        "ntl/ln_NTLpc.csv": "prov_id",
        "satelliteEmbeddings/satelliteEmbeddings2017.csv": "prov_id",
        "satelliteEmbeddings/satelliteEmbeddings2017popWeighted.csv": "prov_id",
        "datasets/sdgs_satelliteEmbeddings2017.csv": "prov_id",
    }
    ok = True
    for f, key in files.items():
        d = pd.read_csv(p_out(*f.split("/")))
        good = len(d) == 112 and d[key].nunique() == 112
        ok &= good
        print(f"  {'OK ' if good else 'BAD'} {f:55} rows={len(d)} uniq_prov={d[key].nunique()}")

    # conservation: province pop2020 (sum) == sum of municipal pop2020
    mun_pop = pd.read_csv(p_in("pop", "pop.csv"))
    prov_pop = pd.read_csv(p_out("pop", "pop.csv"))
    cons = abs(mun_pop["pop2020"].sum() - prov_pop["pop2020"].sum()) < 1e-6
    print(f"  {'OK ' if cons else 'BAD'} pop2020 conservation: mun_total={mun_pop['pop2020'].sum():.0f} "
          f"prov_total={prov_pop['pop2020'].sum():.0f}")

    # population_2020 column now equals INE pop2020 (= sum of municipal pop2020), per pop/pop.csv
    psv = pd.read_csv(p_out("sdgVariables", "sdgVariables.csv"))
    ppop2020 = pd.read_csv(p_out("pop", "pop.csv")).set_index("prov_id")["pop2020"]
    pop_match = (psv.set_index("prov_id")["population_2020"].astype(float).round()
                 == ppop2020.round()).all()
    print(f"  {'OK ' if pop_match else 'BAD'} population_2020 == INE pop2020 for all provinces "
          f"(min={int(psv['population_2020'].min())}; was 1712 under the Atlas count)")

    # bounds: every non-imputed SDG weighted mean within municipal [min,max] (sdg.csv + sdgVariables)
    inb, nbad = True, 0
    for sub, fname in [("sdg", "sdg.csv"), ("sdgVariables", "sdgVariables.csv")]:
        mun = pd.read_csv(p_in(sub, fname)).merge(xwalk[["asdf_id", "prov_id"]], on="asdf_id")
        prov = pd.read_csv(p_out(sub, fname))
        cols = [c for c in prov.columns if is_sdg_family(c) and not c.endswith("_imputed")]
        for c in cols:
            bnd = mun.groupby("prov_id")[c].agg(["min", "max"])
            v = prov.set_index("prov_id")[c].astype(float)
            fc = c + "_imputed"
            imp = (prov.set_index("prov_id")[fc].astype(bool) if fc in prov.columns
                   else pd.Series(False, index=v.index))
            chkmask = v.notna() & ~imp
            bad = chkmask & ~((v >= bnd["min"] - 1e-6) & (v <= bnd["max"] + 1e-6))
            if bad.any():
                inb = False
                nbad += int(bad.sum())
    print(f"  {'OK ' if inb else 'BAD'} every non-imputed SDG weighted mean within municipal [min,max]"
          + ("" if inb else f"  ({nbad} violations)"))

    # imputation: all-NaN SDG cells filled & flagged, none left, each within its department's range
    flagcols = [c for c in psv.columns if c.endswith("_imputed")]
    n_imp = int(psv[flagcols].astype(bool).sum().sum()) if flagcols else 0
    datacols = [c for c in psv.columns if is_sdg_family(c) and not c.endswith("_imputed")]
    n_nan = int(psv[datacols].isna().sum().sum())
    dep = xwalk.drop_duplicates("prov_id").set_index("prov_id")["dep_id"]
    depser = psv["prov_id"].map(dep)
    imp_ok = True
    for fc in flagcols:
        c = fc[:-len("_imputed")]
        for idx in psv.index[psv[fc].astype(bool)]:
            donors = psv.loc[(depser == depser[idx]) & (~psv[fc].astype(bool)), c].astype(float)
            val = float(psv.at[idx, c])
            if donors.empty or not (donors.min() - 1e-6 <= val <= donors.max() + 1e-6):
                imp_ok = False
    print(f"  {'OK ' if (n_nan == 0 and imp_ok) else 'BAD'} imputation: {n_imp} cells filled & flagged, "
          f"{n_nan} NaN left in sdgVariables SDG cols, all within dept [min,max]")

    # spot-check: Murillo 201 (La Paz) should be high imds (El Alto + La Paz dominate)
    psdg = pd.read_csv(p_out("sdg", "sdg.csv")).set_index("prov_id")["imds"]
    print(f"  spot: Murillo(201) imds={psdg.get(201):.1f}  Litoral(405) imds={psdg.get(405):.1f}")
    allok = ok and cons and pop_match and inb and n_nan == 0 and imp_ok
    print("== %s ==" % ("ALL OK" if allok else "CHECK FAILURES"))


def main():
    print("Stage 0: crosswalk, weights, province regionNames")
    xwalk = load_crosswalk()
    weights = load_weights()
    region_prov = build_region_names(xwalk)
    print("Stage 1: curated data folders")
    build_curated(xwalk, weights)
    build_datasets(region_prov)
    build_maps(xwalk)
    print("Stage 3: master CSV")
    rules_path = p_out("code", "aggregation_rules.csv")
    if not os.path.exists(rules_path):
        generate_master_rules()
        print("  >> aggregation_rules.csv generated — REVIEW/EDIT it, then re-run to aggregate the master.")
    else:
        aggregate_master(xwalk, weights, region_prov)
    build_gdp()
    verify(xwalk, weights)


if __name__ == "__main__":
    main()
