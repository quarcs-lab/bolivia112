/**
 * AGGREGATE SATELLITE EMBEDDINGS TO PROVINCE BOUNDARIES
 * ---------------------------------------------------------------------
 * Objective: Compute 64-dimensional mean embeddings for the 112 provinces.
 *
 * 1. Performance: Removed .clip() to prevent timeouts.
 * 2. Logic: Generated band names client-side to fix "Invalid value (selectors)" error.
 * 3. Best Practice: Strict column selection to minimize memory usage.
 */

// --- 1. DATA INPUTS & CLEANING ---

// Province Boundaries (112 provinces)
// We strictly select 'prov_id' to drop heavy attributes we don't need.
// NOTE: You must FIRST upload the province boundary asset to your own Earth
// Engine account, then point the path below at it. Replace <user> with your EE
// username (e.g. 'users/<user>/bolivia112_provinces', or use a
// 'projects/<your-project>/assets/...' path). The asset must contain the
// 'prov_id' attribute (3-digit INE province code, e.g. 405 = Litoral).
var admBoundaries = ee.FeatureCollection("users/<user>/bolivia112_provinces")
  .select(['prov_id']);

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
var exportSelectors = ['prov_id'].concat(bandNames);


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
  description: 'Bolivia112_Province_Embeddings_Mean_2017',
  folder: 'gee',
  fileNamePrefix: 'bolivia112_province_embeddings_2017',
  fileFormat: 'CSV',
  selectors: exportSelectors 
});

// --- DIAGNOSTICS ---

print('Workflow complete. Open the "Tasks" tab to run the export.');
print('Columns to be exported:', exportSelectors);

// Visual Sanity Check
Map.centerObject(admBoundaries, 6);
Map.addLayer(embeddings2017, {bands: ['A00', 'A01', 'A02'], min: -0.1, max: 0.1}, 'Embeddings (RGB)');
Map.addLayer(admBoundaries.style({color: 'red', fillColor: '00000000'}), {}, 'Province Boundaries');