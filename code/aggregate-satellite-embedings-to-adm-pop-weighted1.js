/**
 * SPATIAL DATA SCIENCE WORKFLOW: POPULATION-WEIGHTED EMBEDDINGS (CORRECTED)
 * ---------------------------------------------------------------------
 * OBJECTIVE:
 * Compute the "population-weighted average embedding" for the 112 provinces
 * (admin units) of Bolivia.
 * * CORRECTION APPLIED:
 * - High-Resolution Mass Conservation: Population is downsampled to 10m
 * to match the embeddings, preventing aliasing/sampling errors.
 */

// =====================================================================
// 1. DATA INPUTS & SELECTION
// =====================================================================

// NOTE: You must first upload the 112-province boundary asset to your own
// Earth Engine account and repoint the path below to it. The asset must expose
// a 'prov_id' property (3-digit INE province code, e.g. 405 = Litoral).
// Replace 'users/<user>/bolivia112_provinces' with your actual asset path.
var admBoundaries = ee.FeatureCollection("users/<user>/bolivia112_provinces")
  .select(['prov_id']);

var satEmbeddingsCol = ee.ImageCollection('GOOGLE/SATELLITE_EMBEDDING/V1/ANNUAL');

var worldPop = ee.ImageCollection("WorldPop/GP/100m/pop")
  .filterDate('2017-01-01', '2018-01-01')
  .mosaic()
  .select('population')
  .unmask(0); 

// =====================================================================
// 2. UTILITIES & PRE-PROCESSING
// =====================================================================

// Generate band names (A00...A63)
var bandNames = [];
for (var i = 0; i < 64; i++) {
  var str = i < 10 ? 'A0' + i : 'A' + i; 
  bandNames.push(str);
}

// Create the embedding mosaic
// Sorted to ensure reproducibility
var embeddings = satEmbeddingsCol
  .filterDate('2017-01-01', '2018-01-01')
  .sort('system:index') 
  .mosaic();

// =====================================================================
// 3. RESOLUTION ALIGNMENT (CRITICAL STEP)
// =====================================================================

// 1. Get the native projection/scale of the embeddings (approx 10m)
// We treat the embeddings as the "Master" grid.
var embProj = embeddings.select(0).projection();
var nativeScale = 10; // We define this explicitly for reduction later

// 2. Resample WorldPop to match Embeddings (Mass Conservation)
// Logic: 
// - WorldPop is ~100m. Embeddings are ~10m.
// - 1 WorldPop pixel covers approx 100 Embedding pixels (10x10).
// - To conserve total population, we divide the 100m count by 100
//   when spreading it across the 10m pixels.
var popAreaRatio = 100; // (100m / 10m)^2

var popHighRes = worldPop
  .reproject({
    crs: embProj,
    scale: nativeScale
  })
  .divide(popAreaRatio) 
  .rename('pop_split');

// =====================================================================
// 4. VECTOR ALGEBRA (THE NUMERATOR)
// =====================================================================

// 1. Broadcast Multiply: (Embeddings * Resampled Population)
// Operations now happen at 10m resolution
var weightedEmbeddings = embeddings.multiply(popHighRes);

// 2. Rename to avoid confusion later
var weightedNames = bandNames.map(function(name) { return name + '_sum' });
weightedEmbeddings = weightedEmbeddings.select(bandNames, weightedNames);

// 3. Stack the Denominator
// We use the resampled 'pop_split' as the denominator
var analysisImage = weightedEmbeddings.addBands(popHighRes.rename('pop_sum'));

// =====================================================================
// 5. SPATIAL AGGREGATION
// =====================================================================

/**
 * METHODOLOGY NOTE:
 * We now reduce at scale: 10. This utilizes every pixel of the embedding.
 * Warning: This is ~100x more computationally expensive than scale: 100.
 */

var sums = analysisImage.reduceRegions({
  collection: admBoundaries,
  reducer: ee.Reducer.sum(), 
  scale: nativeScale, // <--- CHANGED TO 10
  tileScale: 16       // <--- MAXIMIZED for memory safety
});

// =====================================================================
// 6. POST-PROCESSING (THE DIVISION)
// =====================================================================

var finalData = sums.map(function(feature) {
  
  var totalPop = feature.getNumber('pop_sum');
  var means = {};
  
  // Client-side loop for instruction generation
  for (var i = 0; i < 64; i++) {
    var numName = weightedNames[i];
    var targetName = bandNames[i];
    
    var numerator = feature.getNumber(numName);
    
    // Calculate Mean (Numerator / Denominator)
    // Safe division isn't strictly necessary if we filter pop > 0 later,
    // but .divide is standard.
    var val = numerator.divide(totalPop);
    
    means[targetName] = val;
  }
  
  // Return clean feature
  return feature
    .select(['prov_id', 'pop_sum'])
    .set(means);
});

// Filter out features with 0 population
finalData = finalData.filter(ee.Filter.gt('pop_sum', 0));

// =====================================================================
// 7. EXPORT
// =====================================================================

var finalSelectors = ['prov_id', 'pop_sum'].concat(bandNames);

Export.table.toDrive({
  collection: finalData,
  description: 'Bolivia112_Provinces_Embeddings_PopWeighted_HighRes_2017',
  folder: 'gee',
  fileNamePrefix: 'bolivia112_provinces_pop_weighted_10m_2017',
  fileFormat: 'CSV',
  selectors: finalSelectors
});

// Print first element to check structure (do not print all, it will timeout)
print('Workflow ready. First feature sample:', finalData.limit(1));