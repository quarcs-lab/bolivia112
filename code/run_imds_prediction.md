# Predicting Provincial Sustainable Development Index (IMDS) Using Satellite Embeddings

## Overview

This analysis predicts the **IMDS** — the population-weighted **provincial** aggregate of the
municipal *Índice Municipal de Desarrollo Sostenible*, a composite index that combines all
Sustainable Development Goal (SDG) indicators into a single development score — using
64-dimensional satellite imagery embeddings from Google Earth Engine.

At the province level, the IMDS measures sustainable development across Bolivia's **112
provinces**, making it a useful target for understanding how satellite-derived features capture
overall development patterns once the 339 municipalities are aggregated.

> **⚠️ Small-sample caveat:** with only **112 provinces** (89 train / 23 test), machine-learning
> estimates — especially the single-split test R² — are far less stable than at the municipal
> level (339 units). The cross-validation R² is the more reliable performance summary here. All
> province values are **population-weighted aggregations** of the underlying municipal data
> (intensive variables = weighted mean, extensive = sum); see
> [`../province_aggregation_report.md`](../province_aggregation_report.md).

## Data Description

| Dataset | Source | Observations |
| --- | --- | --- |
| SDG Data (IMDS) | sdg/sdg.csv | 112 provinces |
| Satellite Embeddings | satelliteEmbeddings/satelliteEmbeddings2017.csv | 112 provinces (64 features) |
| Region Names | regionNames/regionNames.csv | 112 provinces |

All datasets join on **`prov_id`**.

### Target Variable: IMDS

- **Range**: 37.41 to 73.70
- **Mean**: 52.04 ± 7.03
- **Description**: A normalized composite index (0–100 scale) combining all SDG indicators into
  a single measure of provincial sustainable development.

## Methodology

### Model Configuration

| Parameter | Value | Rationale |
| --- | --- | --- |
| Algorithm | Random Forest Regressor | Handles high-dimensional data, captures non-linear relationships |
| n_estimators | 100 | Memory-efficient while maintaining accuracy |
| max_depth | 20 | Prevents overfitting while allowing complex patterns |
| min_samples_split | 5 | Standard regularization |
| min_samples_leaf | 2 | Ensures leaf nodes have sufficient samples |
| max_features | sqrt | ~8 features per split for decorrelated trees |

### Data Split

- **Training set**: 89 provinces (80%)
- **Test set**: 23 provinces (20%)
- **Cross-validation**: 5-fold on training set

## Results

### Model Performance

| Metric | Training Set | Test Set |
| --- | --- | --- |
| R² Score | 0.8382 | −0.0642 |
| RMSE | 2.68 | 8.60 |
| MAE | 1.97 | 6.35 |

The negative single-split test R² is a symptom of the very small test set (23 provinces) — a
single hard-to-predict urban province (e.g. Murillo) dominates the error. Cross-validation gives
a more representative picture.

### Cross-Validation Results

| Fold | R² Score |
| --- | --- |
| 1 | 0.3698 |
| 2 | 0.3716 |
| 3 | 0.2776 |
| 4 | 0.4271 |
| 5 | −0.1007 |
| **Mean** | **0.2691 (±0.1910)** |

## Feature Importance Analysis

### Top 10 Most Important Features

| Rank | Feature | Importance | Cumulative % |
| --- | --- | --- | --- |
| 1 | A57 | 0.0383 | 3.83% |
| 2 | A42 | 0.0375 | 7.58% |
| 3 | A30 | 0.0344 | 11.02% |
| 4 | A52 | 0.0338 | 14.40% |
| 5 | A13 | 0.0328 | 17.68% |
| 6 | A48 | 0.0321 | 20.90% |
| 7 | A21 | 0.0316 | 24.06% |
| 8 | A06 | 0.0300 | 27.06% |
| 9 | A47 | 0.0280 | 29.86% |
| 10 | A33 | 0.0276 | 32.62% |

### Key Insight
- **41 out of 64 features (64.1%)** are needed to capture 80% of the model's predictive power.
- As at the municipal level, overall sustainable development is captured by a broad range of
  satellite-derived features, rather than concentrating in a handful of dimensions.

## Prediction Error Analysis

### Most Overpredicted Provinces
(Model predicts higher development than actual)

| Province | Department | Actual IMDS | Predicted IMDS | Error |
| --- | --- | --- | --- | --- |
| Bolívar | Cochabamba | 42.20 | 54.85 | −12.65 |
| Alonso de Ibáñez | Potosí | 42.60 | 51.70 | −9.10 |
| Chayanta | Potosí | 39.97 | 48.87 | −8.90 |
| Tapacarí | Cochabamba | 39.40 | 47.16 | −7.76 |
| Mizque | Cochabamba | 43.94 | 50.91 | −6.97 |

**Pattern**: predominantly rural highland provinces where satellite features capture physical
infrastructure or land patterns that don't translate into actual development outcomes (harsh
climate, isolation, limited service access).

### Most Underpredicted Provinces
(Model predicts lower development than actual)

| Province | Department | Actual IMDS | Predicted IMDS | Error |
| --- | --- | --- | --- | --- |
| Murillo | La Paz | 72.72 | 50.96 | +21.76 |
| Oropeza | Chuquisaca | 67.18 | 45.51 | +21.67 |
| Sud Chichas | Potosí | 59.20 | 49.76 | +9.44 |
| Gran Chaco | Tarija | 62.97 | 55.11 | +7.86 |
| Capinota | Cochabamba | 52.97 | 46.81 | +6.16 |

**Pattern**: the most urban provinces are systematically underpredicted. **Murillo** (La Paz /
El Alto) and **Oropeza** (Sucre) — the seats of national and departmental government — are each
underpredicted by ~22 points, mirroring the municipal-level result for La Paz. Satellite
embeddings do not fully capture the institutional, economic, and service-related concentration
of development in major urban centers.

## Interpretation

### Why is the explained variance modest?

The IMDS is a **composite index** aggregating diverse dimensions across all SDGs — institutional
(governance, justice), service delivery (health, education), economic (employment, banking),
environmental (emissions, protected areas), and social (gender equality, inequality). Many of
these are **not directly observable from satellite imagery**, so a satellite-only model captures
only the physical manifestations of development.

### Urban–rural divide

The errors reveal a systematic **urban–rural divide**, unchanged by aggregation to provinces:

- **Urban provinces underpredicted** — Murillo and Oropeza achieve far higher development than
  their physical footprint suggests (institutional services, economic opportunity).
- **Rural highland provinces overpredicted** — visible infrastructure does not always translate
  to development outcomes (isolation, climate, service access).

### Note on aggregating to provinces

Aggregation smooths within-province heterogeneity: extreme municipalities are blended into their
province's population-weighted mean, and the sample shrinks from 339 to 112. This both reduces
noise and shrinks the data available for learning — hence the wide cross-validation spread.

## Files Generated

Running `run_imds_prediction.py` writes the following into `code/` (not version-controlled):

| File | Description |
| --- | --- |
| `imds_prediction_results.png` | Comprehensive 6-panel visualization |
| `imds_test_predictions.csv` | Detailed predictions for all test provinces |
| `imds_feature_importance.csv` | Feature importance rankings for all 64 embeddings |
| `imds_model_summary.csv` | Model configuration and performance summary |

## Conclusion

Satellite embeddings explain a **modest share of the variance in provincial sustainable
development (IMDS)** in Bolivia — cross-validation R² ≈ **0.27**, with an unstable single-split
test R² due to the small 23-province test set. As at the municipal level:

- **Urban provinces are underpredicted** — cities achieve higher development than satellite
  features suggest.
- **Rural highlands are overpredicted** — visible infrastructure does not always translate to
  development outcomes.
- **Feature importance is distributed** — overall development requires many satellite features.

Satellite-based predictions are most useful for identifying broad spatial patterns, prioritizing
areas for detailed surveys, and complementing (not replacing) traditional development indicators.

---

## Technical Details

**Script**: `run_imds_prediction.py`

**Dependencies**: pandas · numpy · matplotlib · seaborn · scikit-learn

**Random State**: 42 (for reproducibility)

**Unit of analysis**: 112 Bolivian provinces (population-weighted aggregates of 339 municipalities).
