---
jupytext:
  cell_metadata_filter: -_sphinx_cell_id
  formats: ipynb,md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.19.1
kernelspec:
  display_name: bolivia112
  language: python
  name: python3
---

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/quarcs-lab/bolivia112/blob/main/notebooks/gdp_validation.ipynb)

# Validation: do the aggregated SDG indicators track economic activity?

**Question.** The province-level data in `bolivia112` is a population-weighted aggregation of the 339
municipalities in [`ds4bolivia`](https://github.com/quarcs-lab/ds4bolivia) up to **112 provinces** (see
[`../province_aggregation_report.md`](../province_aggregation_report.md) and the statistical audit in
[`../sdg_aggregation_audit.md`](../sdg_aggregation_audit.md)). If the aggregation preserved meaningful
signal, the aggregated **SDG indices and indicators should be related to economic activity** in the
directions economic theory predicts. We test that here against **GDP per capita (2017)**.

**Why this is a valid, non-circular test.** GDP per capita comes from `gdp/gdp_perCapita_1990_2024.csv`,
which is **attached as-is from the GADM ADM2 layer** — it is *not* produced by the SDG aggregation
pipeline and does not appear in the master table. So correlating the aggregated SDG data against it is an
**external** check, not a tautology.

**Hypothesis.** The composite SDG indices (`imds`, `index_sdg*`; higher = more sustainable development)
are **positively** correlated with log GDP per capita; the 62 granular indicators are **systematically
signed** (coverage/literacy/services positive; poverty/mortality/disease negative).

**Pass criteria** (evaluated programmatically in the Verdict section):

1. `imds` correlates with log GDP per capita at \|r\| ≥ 0.5.
2. A clear majority of the 16 composite indices are **significantly positive** (p < 0.05).
3. Among indicators with a theoretically unambiguous polarity, ≥ 75 % show the **expected sign**.
4. The median \|r\| across the 62 indicators is at least moderate (≥ 0.2).

> **Note on magnitudes.** This is a 112-unit cross-section; province-level correlations are subject to
> the Modifiable Areal Unit Problem and to the approximate-weighting caveats documented in the audit, so
> *moderate* correlations (r ≈ 0.3–0.6) — consistently signed — are the expected, validating outcome,
> not near-perfect ones.

**Structure.** Part 1 illustrates the **space-time dynamics** of GDP per capita across the 112 provinces
(1990–2024); Part 2 uses the 2017 cross-section to **validate** the aggregated SDG indices and indicators
against it.

## Setup

```{code-cell} ipython3
# Packages not in Google Colab's default environment. Harmless locally (already installed via UV).
!pip install statsmodels -q   # required by plotly's trendline='ols'
```

```{code-cell} ipython3
import numpy as np
import pandas as pd
import plotly.express as px
from scipy.stats import pearsonr, spearmanr

import warnings
warnings.filterwarnings('ignore')

pd.set_option('display.max_rows', 70)
```

## Import data

All tables load from the raw GitHub `main` URLs and join on the province key **`prov_id`**.

```{code-cell} ipython3
BASE = 'https://raw.githubusercontent.com/quarcs-lab/bolivia112/main'

sdg  = pd.read_csv(f'{BASE}/sdg/sdg.csv')                          # imds + 15 composite indices
sv   = pd.read_csv(f'{BASE}/sdgVariables/sdgVariables.csv')        # 62 granular indicators (+ flags)
gdp  = pd.read_csv(f'{BASE}/gdp/gdp_perCapita_1990_2024.csv')      # GDP per capita 1990-2024 (target)
defs = pd.read_csv(f'{BASE}/definitions_bolivia112_v20260622.csv') # variable labels

# Human-readable labels for plots; add the two GDP labels (not in the definitions file).
data_dict = dict(zip(defs['varname'], defs['varlabel']))
data_dict['gdppc2017'] = 'GDP per capita, 2017'
data_dict['lngdp2017'] = 'Log GDP per capita, 2017'

# Merge the target onto the SDG tables and build the log target.
df = (gdp[['prov_id', 'prov', 'dep', 'dep_id', 'gdppc2017']]
      .merge(sdg, on='prov_id')
      .merge(sv,  on='prov_id'))
df['lngdp2017'] = np.log(df['gdppc2017'])

print(f'{df.shape[0]} provinces, {df.shape[1]} columns')
df[['prov_id', 'prov', 'dep', 'gdppc2017', 'lngdp2017', 'imds']].head(3)
```

```{code-cell} ipython3
# Column groups under test.
INDEX_COLS = ['imds'] + [c for c in sdg.columns if c.startswith('index_sdg')]
VAR_COLS   = [c for c in sv.columns if c.startswith('sdg') and not c.endswith('_imputed')]
print(f'{len(INDEX_COLS)} composite indices, {len(VAR_COLS)} granular indicators')
```

## Space-time dynamics of GDP per capita (1990–2024)

Before the validation, we look at how province GDP per capita evolves over the full 35-year panel — in
**levels** and in **logs** — to see the growth path, the spread across provinces, and the shape of the
distribution.

```{code-cell} ipython3
# Reshape the 35 yearly columns into a long panel: one row per province-year.
year_cols = [c for c in gdp.columns if c.startswith('gdppc')]
long = gdp.melt(id_vars=['prov_id', 'prov', 'dep', 'dep_id'], value_vars=year_cols,
                var_name='year', value_name='gdppc')
long['year']    = long['year'].str.replace('gdppc', '').astype(int)
long['lngdppc'] = np.log(long['gdppc'])
print(f"{long['prov_id'].nunique()} provinces x {long['year'].nunique()} years = {len(long)} rows "
      f"({long['year'].min()}-{long['year'].max()})")
long.head(3)
```

### Representative provinces — one capital province per department

The capital province of each department (`prov_id` ending in `01`). Lines are coloured by **department**
because four of these provinces are all named "Cercado"; hover shows the province name.

```{code-cell} ipython3
caps = long[long['prov_id'] % 100 == 1].sort_values('year')
for ycol, ttl in [('gdppc', 'GDP per capita'), ('lngdppc', 'Log GDP per capita')]:
    fig = px.line(caps, x='year', y=ycol, color='dep', hover_name='prov',
                  labels={'year': 'Year', 'gdppc': 'GDP per capita',
                          'lngdppc': 'Log GDP per capita', 'dep': 'Department'},
                  title=f"{ttl} of each department's capital province, 1990-2024")
    fig.show()
```

### Evolution of the cross-province distribution — percentiles

Percentiles `p10/25/50/75/90` computed across the 112 provinces in each year.

```{code-cell} ipython3
QS = [0.10, 0.25, 0.50, 0.75, 0.90]
for ycol, ttl in [('gdppc', 'GDP per capita'), ('lngdppc', 'Log GDP per capita')]:
    pct = (long.groupby('year')[ycol].quantile(QS).unstack()
           .rename(columns={q: f'p{int(round(q * 100))}' for q in QS})
           .reset_index()
           .melt(id_vars='year', var_name='percentile', value_name=ycol))
    fig = px.line(pct, x='year', y=ycol, color='percentile',
                  labels={'year': 'Year', 'gdppc': 'GDP per capita',
                          'lngdppc': 'Log GDP per capita', 'percentile': 'Percentile'},
                  title=f'Cross-province percentiles of {ttl.lower()}, 1990-2024')
    fig.show()
```

### Distribution every five years — box plots

```{code-cell} ipython3
BOX_YEARS = list(range(1990, 2021, 5)) + [2024]      # 1990, 1995, ..., 2020, 2024
box = long[long['year'].isin(BOX_YEARS)].copy()
box['year'] = box['year'].astype(str)                 # categorical -> even spacing
for ycol, ttl in [('gdppc', 'GDP per capita'), ('lngdppc', 'Log GDP per capita')]:
    fig = px.box(box, x='year', y=ycol,
                 labels={'year': 'Year', 'gdppc': 'GDP per capita',
                         'lngdppc': 'Log GDP per capita'},
                 title=f'Distribution of {ttl.lower()} across provinces, every 5 years')
    fig.show()
```

### Average across provinces — mean vs median

The cross-province **mean** sits above the **median** in every year: the province distribution is
right-skewed (a few high-GDP provinces pull the mean up).

```{code-cell} ipython3
for ycol, ttl in [('gdppc', 'GDP per capita'), ('lngdppc', 'Log GDP per capita')]:
    agg = (long.groupby('year')[ycol].agg(['mean', 'median'])
           .reset_index()
           .melt(id_vars='year', var_name='statistic', value_name=ycol))
    fig = px.line(agg, x='year', y=ycol, color='statistic',
                  labels={'year': 'Year', 'gdppc': 'GDP per capita',
                          'lngdppc': 'Log GDP per capita', 'statistic': 'Statistic'},
                  title=f'Cross-province {ttl.lower()}: mean vs median, 1990-2024')
    fig.show()
```

**Takeaway.** GDP per capita rose broadly — across every department and across the whole distribution —
from 1990 to 2024, while the spread between percentiles (and the mean–median gap) shows that
**cross-province dispersion persists**. With this space-time picture established, we now validate the
aggregated SDG data against the 2017 cross-section.

## The target: log GDP per capita, 2017

GDP per capita is right-skewed, so we validate against its log (a standard choice that linearizes the
relationship with the 0–100 indices).

```{code-cell} ipython3
df[['gdppc2017', 'lngdp2017']].describe().round(2)
```

```{code-cell} ipython3
px.box(df, x='lngdp2017', y='dep', color='dep', hover_name='prov',
       points='all', labels=data_dict,
       title='Log GDP per capita (2017) across departments')
```

## Helper: correlation against the target

For each variable we compute Pearson and Spearman correlations with `lngdp2017`, with p-values and the
effective sample size. Following the audit, a variable's **imputed provinces are excluded** from its own
correlation (each `<var>_imputed` flag marks fabricated cells that must not enter inference).

```{code-cell} ipython3
def corr_table(frame, target, cols):
    """Pearson/Spearman of each col vs target, excluding that col's imputed provinces."""
    rows = []
    for c in cols:
        sub = frame[[target, c]]
        flag = c + '_imputed'
        if flag in frame.columns:                       # drop imputed cells (audit guidance)
            sub = sub[~frame[flag].fillna(False).astype(bool)]
        sub = sub.dropna()
        if len(sub) < 5 or sub[c].nunique() < 3:
            continue
        r, p   = pearsonr(sub[target], sub[c])
        rho, _ = spearmanr(sub[target], sub[c])
        rows.append({'variable': c, 'label': data_dict.get(c, c), 'n': len(sub),
                     'pearson_r': r, 'pearson_p': p, 'spearman_r': rho, 'abs_r': abs(r)})
    return (pd.DataFrame(rows)
            .sort_values('abs_r', ascending=False)
            .reset_index(drop=True))
```

## Validation A — composite SDG indices vs GDP

These 16 indices are normalised so that **higher = better**; every one should correlate **positively**
with log GDP per capita.

```{code-cell} ipython3
tbl_idx = corr_table(df, 'lngdp2017', INDEX_COLS)
tbl_idx.round(3)
```

```{code-cell} ipython3
px.bar(tbl_idx.sort_values('pearson_r'),
       x='pearson_r', y='variable', orientation='h',
       color='pearson_r', color_continuous_scale='RdBu', range_color=[-1, 1],
       hover_data=['label', 'n', 'spearman_r', 'pearson_p'], labels=data_dict,
       title='Correlation of each SDG index with log GDP per capita (2017)')
```

```{code-cell} ipython3
# imds — the headline composite — and the two strongest indices, with OLS trendlines.
headline = ['imds'] + [v for v in tbl_idx['variable'] if v != 'imds'][:2]
for v in headline:
    fig = px.scatter(df, x=v, y='lngdp2017', color='dep', hover_name='prov',
                     trendline='ols', trendline_scope='overall', labels=data_dict,
                     title=f'{data_dict.get(v, v)}  vs  log GDP per capita (2017)')
    fig.show()
```

## Validation B — granular SDG indicators vs GDP

The 62 indicators are **mixed-direction** (some measure "goods" like coverage, some "bads" like poverty
or mortality), so we rank them by the **magnitude** of correlation, |r|.

```{code-cell} ipython3
tbl_var = corr_table(df, 'lngdp2017', VAR_COLS)
print(f'{len(tbl_var)} indicators evaluated  |  median |r| = {tbl_var.abs_r.median():.3f}'
      f'  |  significant (p<0.05): {(tbl_var.pearson_p < 0.05).sum()}/{len(tbl_var)}')
tbl_var.round(3)
```

```{code-cell} ipython3
# Top 20 indicators by strength of association (sign shown by colour).
top = tbl_var.head(20).sort_values('pearson_r')
px.bar(top, x='pearson_r', y='variable', orientation='h',
       color='pearson_r', color_continuous_scale='RdBu', range_color=[-1, 1],
       hover_data=['label', 'n', 'spearman_r'], labels=data_dict,
       title='Top 20 SDG indicators by |correlation| with log GDP per capita (2017)')
```

```{code-cell} ipython3
# Strongest positive and strongest negative correlates, with OLS trendlines.
strongest_pos = tbl_var[tbl_var.pearson_r > 0].iloc[0]['variable']
strongest_neg = tbl_var[tbl_var.pearson_r < 0].iloc[0]['variable']
for v in [strongest_pos, strongest_neg]:
    fig = px.scatter(df, x=v, y='lngdp2017', color='dep', hover_name='prov',
                     trendline='ols', trendline_scope='overall', labels=data_dict,
                     title=f'{data_dict.get(v, v)}  vs  log GDP per capita (2017)')
    fig.show()
```

## Direction check

For the indicators whose polarity is theoretically unambiguous, does the **sign** of the correlation
match expectation? (`+1` = expected to rise with GDP, `-1` = expected to fall with GDP.) CO₂-per-capita
indicators are marked `+1`: they are environmental disamenities but mechanically rise with economic
activity, so a positive correlation is the GDP-tracking expectation.

A near-zero, statistically **insignificant** correlation (r ≈ 0) is *uninformative*, not "wrong" — its
sign is just noise. So the headline metric is the sign-match rate among indicators that are
**significantly** correlated with GDP (p < 0.05); the all-indicators rate is reported alongside for
transparency.

```{code-cell} ipython3
EXPECTED_SIGN = {
    # higher = more developed / richer  -> expected POSITIVE
    'sdg1_4_abs': +1, 'sdg3_1_idca': +1, 'sdg4_4_phe': +1, 'sdg4_6_lr': +1,
    'sdg4_c_qti': +1, 'sdg4_c_qts': +1, 'sdg6_1_dwc': +1, 'sdg6_2_sc': +1, 'sdg6_3_wwt': +1,
    'sdg7_1_ec': +1, 'sdg7_1_rec': +1, 'sdg7_1_cce': +1, 'sdg8_10_dbb': +1,
    'sdg9_5_cd': +1, 'sdg9_5_eutf': +1, 'sdg9_c_mnc': +1, 'sdg9_c_drb': +1, 'sdg11_2_samt': +1,
    'sdg16_9_cr': +1, 'sdg17_1_pmtax': +1, 'sdg17_5_pipc': +1,
    'sdg7_3_co2epc': +1, 'sdg13_2_tco2e': +1,
    # higher = less developed / poorer  -> expected NEGATIVE
    'sdg1_1_eepr': -1, 'sdg1_1_ubn': -1, 'sdg1_2_mpi': -1, 'sdg2_2_cmc': -1,
    'sdg3_2_imr': -1, 'sdg3_2_mrc': -1, 'sdg3_3_cdir': -1, 'sdg3_3_ti': -1,
    'sdg3_3_imr': -1, 'sdg3_3_di': -1, 'sdg3_7_afr': -1,
    'sdg4_1_ssdrm': -1, 'sdg4_1_ssdrf': -1, 'sdg8_4_rem': -1, 'sdg8_6_mlm': -1, 'sdg8_6_wlm': -1,
    'sdg10_2_gcye': -1, 'sdg10_2_iec': -1, 'sdg11_1_hocr': -1, 'sdg11_1_hno': -1, 'sdg13_1_ccvi': -1,
}

chk = tbl_var[tbl_var.variable.isin(EXPECTED_SIGN)].copy()
chk['expected'] = chk['variable'].map(EXPECTED_SIGN)
chk['observed'] = np.sign(chk['pearson_r']).astype(int)
chk['sign_ok']  = chk['expected'] == chk['observed']
chk['signif']   = chk['pearson_p'] < 0.05

sig    = chk[chk['signif']]                       # significantly correlated with GDP
sig_ok = int(sig['sign_ok'].sum())
print(f'Indicators with an unambiguous expected sign : {len(chk)}')
print(f'  significantly correlated with GDP (p<0.05) : {len(sig)}')
print(f'  of those, sign MATCHES expectation         : {sig_ok}/{len(sig)} ({sig_ok/len(sig):.0%})')
print(f'  (all expected-sign incl. weak/insignificant: '
      f'{int(chk.sign_ok.sum())}/{len(chk)} = {chk.sign_ok.mean():.0%})')

exc = sig[~sig['sign_ok']][['variable', 'label', 'expected', 'pearson_r', 'pearson_p']]
print('\nSignificant exceptions (significant, but opposite to the naive expectation):')
exc.round(3) if len(exc) else 'none — every significant indicator points the expected way'
```

## Caveats

- **Imputed cells excluded.** Each indicator's correlation drops its own `<var>_imputed` provinces
  (8 fabricated cells total). See [`../sdg_aggregation_audit.md`](../sdg_aggregation_audit.md) finding 5.
- **Approximate weights.** 36 of 62 indicators are population-weighted approximations of non-population
  rates — see [`../sdgVariables/sdg_reference_populations.csv`](../sdgVariables/sdg_reference_populations.csv)
  (`weight_is_approximate`) and [`../code/sdg_aggregation_sensitivity.csv`](../code/sdg_aggregation_sensitivity.csv).
  This adds noise that *attenuates* correlations, so observed associations are conservative.
- **MAUP / cross-section.** 112-unit province correlations are scale-dependent and must not be read as
  municipal or individual relationships; 15 provinces are single-municipality passthroughs.
- **Independent target.** GDP per capita is GADM-attached, so this validation is not circular.

## Verdict

```{code-cell} ipython3
imds_r       = float(tbl_idx.loc[tbl_idx.variable == 'imds', 'pearson_r'].iloc[0])
idx_pos_sig  = int(((tbl_idx.pearson_r > 0) & (tbl_idx.pearson_p < 0.05)).sum())
n_idx        = len(tbl_idx)
sig          = chk[chk['signif']]                 # significantly correlated, unambiguous-sign subset
sign_ok_frac = float(sig['sign_ok'].mean())       # share with the expected sign
var_med_absr = float(tbl_var.abs_r.median())

c1 = abs(imds_r) >= 0.5
c2 = idx_pos_sig >= 0.6 * n_idx          # clear majority of indices significantly positive
c3 = sign_ok_frac >= 0.80                # expected sign among significantly-correlated indicators
c4 = var_med_absr >= 0.20

print('VALIDATION CRITERIA')
print(f'  1. |corr(imds, lnGDP)| = {abs(imds_r):.2f}  >= 0.50 ................. {"PASS" if c1 else "FAIL"}')
print(f'  2. indices sig. positive = {idx_pos_sig}/{n_idx}  (>= 60%) ............. {"PASS" if c2 else "FAIL"}')
print(f'  3. expected sign among significant indicators = {sign_ok_frac:.0%}  (>= 80%) . {"PASS" if c3 else "FAIL"}')
print(f'  4. median |r| of 62 indicators = {var_med_absr:.2f}  (>= 0.20) ........ {"PASS" if c4 else "FAIL"}')

passed = sum([c1, c2, c3, c4])
print('\n' + '=' * 72)
if passed == 4:
    print('VERDICT: PASS — the aggregated SDG indices and indicators are systematically')
    print('and significantly related to independent GDP per capita in the theoretically')
    print('expected directions. The municipality -> province aggregation preserves')
    print('economically meaningful signal. Magnitudes are moderate, as expected for a')
    print('112-province cross-section under the documented weighting caveats.')
else:
    print(f'VERDICT: PARTIAL — {passed}/4 criteria met. The aggregation shows the expected')
    print('association with GDP on the criteria that passed; review the failing criteria')
    print('above (likely environment-oriented indices or attenuation from approximate weights).')
print('=' * 72)
```
