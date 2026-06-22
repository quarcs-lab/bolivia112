#!/usr/bin/env python3
"""SDG aggregation sensitivity diagnostics (read-only).

Empirical backbone of the statistical audit in `sdg_aggregation_audit.md`. It quantifies how the
municipality -> province aggregation of the SDG indicators/indices depends on the WEIGHTING choice,
so the audit's claims are evidence-based rather than asserted.

For every SDG indicator (`sdgVariables.csv`) and index (`sdg.csv`) it recomputes the 112 province
values under three weightings of the municipal values:
  * unweighted  - simple municipal mean
  * pop2020     - population-weighted mean   [the current build choice]
  * area        - land-area-weighted mean (municipal `modis_total_area` pixel count)
and reports, per variable: max |Delta| (pop vs unweighted), the same relative to the cross-province
range, Pearson & Spearman correlation across the 112 provinces, and how many provinces move >= 5 rank
positions. For the three areal-denominator rates it additionally reports pop- vs area-weighting.

It also reports the municipal SUPPORT behind each value (how many municipalities had data), the
single-municipality "provinces" (exact passthroughs), and the imputed cells.

Writes `code/sdg_aggregation_sensitivity.csv`. Run:
    uv run python code/audit_sdg_aggregation.py
"""
import os
import re

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
B112 = os.path.dirname(HERE)
DS4 = next((p for p in [os.path.join(B112, "ds4bolivia"),
                        os.path.join(os.path.dirname(B112), "ds4bolivia")]
            if os.path.isdir(p)), os.path.join(os.path.dirname(B112), "ds4bolivia"))

AREAL_RATES = ["sdg15_1_pa", "sdg13_2_dra", "sdg15_5_blr"]   # % of land / forest area


def p_in(*a):
    return os.path.join(DS4, *a)


def load():
    rn = pd.read_csv(p_in("regionNames", "regionNames.csv"), dtype={"mun_id": str})
    rn["prov_id"] = rn["mun_id"].str.strip().str[:3].astype(int)
    xw = rn[["asdf_id", "prov_id"]]
    sv = pd.read_csv(p_in("sdgVariables", "sdgVariables.csv"))
    sdg = pd.read_csv(p_in("sdg", "sdg.csv"))
    pop = pd.read_csv(p_in("pop", "pop.csv")).set_index("asdf_id")["pop2020"].astype(float)
    master = pd.read_csv(p_in("ds4bolivia_v20250523.csv"))
    acols = [c for c in master.columns if c.startswith("modis_total_area")]
    area = master.set_index("asdf_id")[acols].mean(axis=1).astype(float)  # ~time-invariant land area
    return xw, sv, sdg, pop, area


def prov_mean(m, col, w):
    """Population/area/uniform weighted mean of `col` by prov_id, renormalized over present data."""
    x = m[col].astype(float)
    wv = m[w].astype(float)
    num = (x * wv).groupby(m["prov_id"]).sum(min_count=1)
    den = wv.where(x.notna()).groupby(m["prov_id"]).sum(min_count=1)
    return num / den


def compare(a, b):
    """Return (max|Δ|, relΔ vs range, pearson, spearman, #provinces moving ≥5 ranks)."""
    both = pd.concat([a.rename("a"), b.rename("b")], axis=1).dropna()
    if len(both) < 3:
        return dict(maxabs=np.nan, reldelta=np.nan, pearson=np.nan, spearman=np.nan, rankshift5=np.nan)
    a2, b2 = both["a"], both["b"]
    rng = a2.max() - a2.min()
    ra, rb = a2.rank(ascending=False), b2.rank(ascending=False)
    return dict(
        maxabs=float((a2 - b2).abs().max()),
        reldelta=float((a2 - b2).abs().max() / rng) if rng else np.nan,
        pearson=float(a2.corr(b2)),
        spearman=float(a2.corr(b2, method="spearman")),
        rankshift5=int(((ra - rb).abs() >= 5).sum()),
    )


def main():
    xw, sv, sdg, pop, area = load()
    n_mun = xw.groupby("prov_id").size()
    single = sorted(n_mun.index[n_mun == 1])
    print(f"DS4 source: {DS4}")
    print(f"municipalities={len(xw)}  provinces={n_mun.size}  "
          f"single-municipality provinces={len(single)}  -> {single}")
    print(f"weight divergence corr(pop2020, land area): "
          f"pearson={pop.reindex(area.index).corr(area):.3f} "
          f"spearman={pop.reindex(area.index).corr(area, method='spearman'):.3f}\n")

    rows = []
    for src, df, kind in [(sv, sv, "indicator"), (sdg, sdg, "index")]:
        m = df.merge(xw, on="asdf_id", how="left")
        m["w_pop"] = m["asdf_id"].map(pop)
        m["w_area"] = m["asdf_id"].map(area)
        m["w_one"] = 1.0
        cols = [c for c in df.columns
                if (c.startswith("sdg") or c.startswith("index_sdg") or c == "imds")]
        for c in cols:
            vp = prov_mean(m, c, "w_pop")
            vu = prov_mean(m, c, "w_one")
            supp = m[c].notna().groupby(m["prov_id"]).sum()
            r = compare(vp, vu)                                  # pop vs unweighted
            row = dict(varname=c, kind=kind, n_prov=int(vp.notna().sum()),
                       min_support=int(supp.min()), median_support=float(supp.median()),
                       n_prov_support1=int((supp == 1).sum()),
                       pop_vs_unweighted_maxabs=r["maxabs"], pop_vs_unweighted_reldelta=r["reldelta"],
                       pearson=r["pearson"], spearman=r["spearman"], rankshift_ge5=r["rankshift5"])
            if c in AREAL_RATES:
                va = prov_mean(m, c, "w_area")
                ra = compare(vp, va)                             # pop vs area
                row.update(area_vs_pop_maxabs=ra["maxabs"], area_vs_pop_spearman=ra["spearman"],
                           area_vs_pop_rankshift_ge5=ra["rankshift5"])
            rows.append(row)

    res = pd.DataFrame(rows)
    out = os.path.join(HERE, "sdg_aggregation_sensitivity.csv")
    res.sort_values(["kind", "spearman"]).to_csv(out, index=False)
    print(f"wrote {os.path.relpath(out, B112)}  ({len(res)} variables)\n")

    print("== Weight sensitivity: most weight-SENSITIVE indicators (pop vs unweighted) ==")
    show = res[res.kind == "indicator"].sort_values("spearman").head(12)
    for _, r in show.iterrows():
        print(f"  {r.varname:14} spearman={r.spearman:.3f}  rankshift>=5: {int(r.rankshift_ge5):3d}/112"
              f"  max|Δ|={r.pop_vs_unweighted_maxabs:.2f} (rel {r.pop_vs_unweighted_reldelta:.0%})")

    print("\n== Areal rates: population- vs AREA-weighting (the implemented fix) ==")
    for c in AREAL_RATES:
        r = res[res.varname == c]
        if len(r):
            r = r.iloc[0]
            print(f"  {c:12} area_vs_pop max|Δ|={r.area_vs_pop_maxabs:.3f}  "
                  f"spearman={r.area_vs_pop_spearman:.3f}  rankshift>=5: {int(r.area_vs_pop_rankshift_ge5)}/112")

    print("\n== Smallest municipal support (most fragile province estimates) ==")
    frag = res[res.kind == "indicator"].sort_values(["min_support", "median_support"]).head(8)
    for _, r in frag.iterrows():
        print(f"  {r.varname:14} min_support={int(r.min_support)}  median_support={r.median_support:.0f}"
              f"  provinces backed by a single municipality: {int(r.n_prov_support1)}")

    print("\n== Imputed cells (all municipalities missing -> department mean) ==")
    m = sv.merge(xw, on="asdf_id", how="left")
    for c in ["sdg1_1_eepr", "sdg8_4_rem", "sdg10_2_iec", "sdg2_4_pual", "sdg2_4_td"]:
        if c not in sv.columns:
            continue
        allnan = [int(p) for p, g in m.groupby("prov_id") if g[c].isna().all()]
        print(f"  {c:14} fully-missing provinces -> {allnan}")
    print("\n(Use sdg_aggregation_sensitivity.csv + sdgVariables/sdg_reference_populations.csv together:"
          " an approximate-weight indicator only matters where it is also weight-sensitive above.)")


if __name__ == "__main__":
    main()
