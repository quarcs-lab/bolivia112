# README: Bolivia Satellite Embeddings (2017) — Province Level

**Dataset Title:** Aggregated Google Satellite Embeddings for Bolivia Provinces (2017)  
**Date Generated:** October 2023  
**Source Platform:** Google Earth Engine (GEE)  
**Source Collection:** `GOOGLE/SATELLITE_EMBEDDING/V1/ANNUAL`  

> **Note:** Each `A00`–`A63` is the **population-weighted mean** of the municipal embeddings, weighted by **`pop2017`**. The municipal embeddings are themselves the spatial mean of the 10 m Google Satellite Embeddings (2017). See **2. Methodology** below and [../province_aggregation_report.md](../province_aggregation_report.md).

## 1. Context & Overview

This dataset contains spatially aggregated "embedding" vectors derived from high-resolution satellite imagery for the provinces of Bolivia for the year 2017.

### Files

**satelliteEmbeddings2017.csv** - Contains 65 columns: one identifier (prov_id) and 64 embedding dimensions (A00-A63) for all 112 provinces.

**satelliteEmbeddings2017popWeighted.csv** - A variant (66 columns) whose municipal embeddings were
**population-weighted within Google Earth Engine** (pixels weighted by WorldPop population) before the
province roll-up; it adds a `pop_sum` column (summed). See **2. Methodology**.

### What are Satellite Embeddings?
Unlike traditional satellite data that provides physical values (e.g., surface reflectance, temperature), these embeddings are the output of a deep learning model (a self-supervised Convolutional Neural Network). 

* **The Input:** The model processes raw Sentinel-2 and Landsat imagery.
* **The Process:** It learns to compress visual information (texture, shapes, colors, road networks, building density) into a compact numerical representation.
* **The Output:** A 64-dimensional vector (an array of 64 numbers) that uniquely characterizes the landscape of a specific location.

### Why use this data?
These 64 variables capture complex spatial patterns that simple indices like NDVI (vegetation) or NTL (nightlights) miss. They are effective for:
* **Poverty Mapping:** Predicting economic indicators based on the built-up environment.
* **Population Estimation:** Correlating texture with population density.
* **Land Use Classification:** Distinguishing between different types of agriculture or urban zoning without manual labeling.

---

## 2. Methodology

1.  **Source Data (generation):** Google Satellite Embeddings V1 Annual Mosaic 2017 — GEE collection
    `GOOGLE/SATELLITE_EMBEDDING/V1/ANNUAL` (a self-supervised CNN over Sentinel-2 + Landsat).
2.  **Resolution:** The native embeddings were computed at approximately **10m resolution**.
3.  **Municipal step (GEE):** the **spatial mean** of each embedding band was computed per municipal
    polygon, using [`../code/aggregate-satellite-embedings-to-adm.js`](../code/aggregate-satellite-embedings-to-adm.js).
    A population-weighted variant,
    [`../code/aggregate-satellite-embedings-to-adm-pop-weighted1.js`](../code/aggregate-satellite-embedings-to-adm-pop-weighted1.js),
    instead weights pixels by **WorldPop GP 100 m (2017)** population (downsampled to 10 m) — this
    produces `satelliteEmbeddings2017popWeighted.csv`.
4.  **Province step (aggregation):** the 339 municipal values are rolled up to the 112 provinces as a
    **population-weighted mean weighted by `pop2017`** (rule `wmean`, weight `2017` in
    [`../code/aggregation_rules.csv`](../code/aggregation_rules.csv), via `build_curated()` in
    [`../code/build_bolivia112.py`](../code/build_bolivia112.py)); the pop-weighted file additionally
    **sums** its `pop_sum` column. See [../province_aggregation_report.md](../province_aggregation_report.md).
5.  **Spatial Scope:** 112 Provinces in Bolivia.

---

## 3. Variable Dictionary

The dataset contains **65 columns**.

| Variable Name | Type | Description |
| :--- | :--- | :--- |
| **prov_id** | String/Int | **Unique Province Identifier.** 3-digit INE province code (e.g. `405` = Litoral). Use this key to join this data back to the province boundaries (`bolivia112provincesFull`) or other socio-economic province datasets. |
| **A00** | Float | **Embedding Dimension 0.** An abstract feature learned by the neural network. |
| **A01** | Float | **Embedding Dimension 1.** An abstract feature learned by the neural network. |
| **...** | ... | ... |
| **A63** | Float | **Embedding Dimension 63.** An abstract feature learned by the neural network. |

### Interpreting the "A" Variables
* **Abstract Nature:** You cannot intuitively say "A05 is vegetation" or "A12 is water." These are latent variables representing high-level visual features.
* **Usage:** They are designed to be used as **features (X)** in machine learning models (e.g., Ridge Regression, Random Forest).
    * *Example Model:* $GDP_{capita} = f(A00, A01, ..., A63)$
* **Similarity:** Locations with similar vectors (Euclidean distance) look similar from space.

---

## 4. Usage Notes

* **Data Completeness:** Always check for `null` values. If a polygon is extremely small or falls outside the satellite coverage (e.g., heavy cloud masking), it may not have a computed mean.
* **Scale:** The values typically range between **-1.0 and 1.0** (standardized output from the neural network), though the mean aggregation may shrink this range.
* **Dimensionality Reduction:** Because 64 variables can be a lot for simple regressions, it is common practice to perform **PCA (Principal Component Analysis)** on columns A00-A63 to reduce them to the top 3-5 "Principal Components" before analysis.

---

## 5. Example Code

You can run the examples below in [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/notebooks/empty.ipynb)

```python
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestRegressor

# Load satellite embeddings (population-weighted province aggregations)
url = "https://raw.githubusercontent.com/quarcs-lab/bolivia112/main/satelliteEmbeddings/satelliteEmbeddings2017.csv"
df_emb = pd.read_csv(url)

# Select the 64 embedding dimensions
embedding_cols = [f'A{str(i).zfill(2)}' for i in range(64)]
X = df_emb[embedding_cols]

# Option 1: Use all 64 dimensions directly
# Load SDG target variable
df_sdg = pd.read_csv("../sdg/sdg.csv")
df_merged = df_emb.merge(df_sdg, on='prov_id')
y = df_merged['index_sdg1']  # Poverty index

# Train a model
rf = RandomForestRegressor(n_estimators=100, random_state=42)
rf.fit(X, y)

# Option 2: Dimensionality reduction with PCA
pca = PCA(n_components=5)
X_pca = pca.fit_transform(X)
print(f"Variance explained by 5 components: {pca.explained_variance_ratio_.sum():.2%}")
```

---

## 6. Citation

If using this data, please cite the source model:

> Google Earth Engine. (2020). *Satellite Embeddings V1*. Available at: https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_SATELLITE_EMBEDDING_V1_ANNUAL

## 7. Google Earth Engine Processing Code

The embeddings are first computed at the **municipal** level in Google Earth Engine (below), and the published province table is then obtained as a **population-weighted mean** of the 339 municipalities into the 112 provinces (see [../province_aggregation_report.md](../province_aggregation_report.md)).

```
/**
 * AGGREGATE SATELLITE EMBEDDINGS TO ADM BOUNDARIES
 * ---------------------------------------------------------------------
 * Objective: Compute 64-dimensional mean embeddings for administrative units.
 *
 * 1. Performance: Removed .clip() to prevent timeouts.
 * 2. Logic: Generated band names client-side to fix "Invalid value (selectors)" error.
 * 3. Best Practice: Strict column selection to minimize memory usage.
 */

// --- 1. DATA INPUTS & CLEANING ---

// Administrative Boundaries (municipalities; province values are a
// downstream population-weighted aggregation of these polygons)
// We strictly select 'asdf_id' to drop heavy attributes we don't need.
var admBoundaries = ee.FeatureCollection("projects/ee-carlosmendez777/assets/bolivia/bolivia339geoqueryFull")
  .select(['asdf_id']); 

// Satellite Embeddings Collection
var satEmbeddingsCol = ee.ImageCollection('GOOGLE/SATELLITE_EMBEDDING/V1/ANNUAL');

// --- 2. CLIENT-SIDE SETUP (THE FIX) ---

// We generate the list of band names (A00...A63) using standard JavaScript.
// This prevents the "Invalid value (selectors)" error by ensuring the 
// Export function gets a concrete list of strings, not a server-side object.
var bandNames = [];
for (var i = 0; i < 64; i++) {
  // Adds a leading zero for single digits (e.g., 'A05') to match GEE naming
  var str = i < 10 ? 'A0' + i : 'A' + i; 
  bandNames.push(str);
}

// Prepare the column order for the CSV: ID first, then the 64 bands
var exportSelectors = ['asdf_id'].concat(bandNames);


// --- 3. PRE-PROCESSING ---

// Step A: Define Timeframe
var start = ee.Date('2017-01-01');
var end   = ee.Date('2018-01-01');

// Step B: Create Seamless Composite
// We filter and mosaic. We do NOT clip here; the reducer handles the geometry.
var embeddings2017 = satEmbeddingsCol
  .filterDate(start, end)
  .mosaic(); 


// --- 4. SPATIAL AGGREGATION ---

// We compute the mean of all 64 bands for each polygon.
// - scale: 10 forces the analysis to native resolution.
// - tileScale: 8 helps process complex geometries without memory errors.
var aggregatedData = embeddings2017.reduceRegions({
  collection: admBoundaries,
  reducer: ee.Reducer.mean(), 
  scale: 10,  
  tileScale: 8 
});


// --- 5. EXPORT ---

// Export to Google Drive
Export.table.toDrive({
  collection: aggregatedData,
  description: 'Bolivia_Embeddings_Mean_2017',
  folder: 'gee', 
  fileNamePrefix: 'bolivia_embeddings_2017',
  fileFormat: 'CSV',
  selectors: exportSelectors 
});

// --- DIAGNOSTICS ---

print('Workflow complete. Open the "Tasks" tab to run the export.');
print('Columns to be exported:', exportSelectors);

// Visual Sanity Check
Map.centerObject(admBoundaries, 6);
Map.addLayer(embeddings2017, {bands: ['A00', 'A01', 'A02'], min: -0.1, max: 0.1}, 'Embeddings (RGB)');
Map.addLayer(admBoundaries.style({color: 'red', fillColor: '00000000'}), {}, 'Boundaries');
```