#!/usr/bin/env python3
"""
Random Forest Model to Predict Extreme Energy Poverty Rate using Satellite Embeddings
Variable: sdg1_1_eepr - Extreme energy poverty rate, 2016 (% of houses)
bolivia112 Project

NOTE: The unit of analysis is now 112 Bolivian provinces (not 339 municipalities).
Province values are population-weighted aggregations of the municipal data
(intensive variables = weighted mean, extensive variables = sum); see
../province_aggregation_report.md. With only 112 observations the sample is small
for ML, so cross-validation/test metrics should be interpreted with caution.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score, KFold, train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import warnings
warnings.filterwarnings('ignore')

print("="*80)
print("RANDOM FOREST MODEL: EXTREME ENERGY POVERTY RATE PREDICTION")
print("bolivia112 - Predicting Energy Poverty from Satellite Embeddings")
print("Target: sdg1_1_eepr (% of houses in extreme energy poverty, 2016)")
print("="*80)

# Define repository URL
REPO_URL = "https://raw.githubusercontent.com/quarcs-lab/bolivia112/main"

# 1. LOAD DATASETS
print("\n[1/8] Loading datasets...")
url_names = f"{REPO_URL}/regionNames/regionNames.csv"
url_sdg_vars = f"{REPO_URL}/sdgVariables/sdgVariables.csv"
url_embeddings = f"{REPO_URL}/satelliteEmbeddings/satelliteEmbeddings2017.csv"

df_names = pd.read_csv(url_names)
df_sdg_vars = pd.read_csv(url_sdg_vars)
df_embeddings = pd.read_csv(url_embeddings)

print(f"  ✓ Loaded {len(df_names)} provinces")
print(f"  ✓ Loaded {len(df_sdg_vars.columns)-1} SDG variables")
print(f"  ✓ Loaded {len(df_embeddings.columns)-1} satellite embedding dimensions")

# 2. DATA PREPARATION
print("\n[2/8] Preparing data...")
df = pd.merge(df_names, df_sdg_vars, on='prov_id', how='inner')
df = pd.merge(df, df_embeddings, on='prov_id', how='inner')

# Check if target variable exists and get related poverty variables
target_var = 'sdg1_1_eepr'
related_vars = ['sdg1_1_ubn', 'sdg1_2_mpi', 'sdg7_1_ec']  # Related poverty measures

embedding_cols = [col for col in df.columns if col.startswith('A')]
df_clean = df[['prov_id', 'prov', 'dep', target_var] + related_vars + embedding_cols].dropna()

print(f"  ✓ Final dataset shape: {df_clean.shape}")
print(f"  ✓ Provinces with data: {len(df_clean)}")
print(f"  ✓ Missing data: {len(df) - len(df_clean)} provinces")
print(f"  ✓ Features: {len(embedding_cols)} satellite embeddings")
print(f"  ✓ Target: {target_var} (Extreme energy poverty rate)")

X = df_clean[embedding_cols].values
y = df_clean[target_var].values

print(f"\n  Target Variable Statistics (% of houses in extreme energy poverty):")
print(f"    Mean: {y.mean():.2f}%")
print(f"    Median: {np.median(y):.2f}%")
print(f"    Min: {y.min():.2f}%")
print(f"    Max: {y.max():.2f}%")
print(f"    Std: {y.std():.2f}%")

# 3. COMPARE WITH RELATED POVERTY MEASURES
print("\n[3/8] Analyzing relationship with other poverty indicators...")

if 'sdg1_1_ubn' in df_clean.columns:
    corr_ubn = df_clean[[target_var, 'sdg1_1_ubn']].corr().iloc[0, 1]
    print(f"  Correlation with Unsatisfied Basic Needs (sdg1_1_ubn): {corr_ubn:.4f}")

if 'sdg1_2_mpi' in df_clean.columns:
    corr_mpi = df_clean[[target_var, 'sdg1_2_mpi']].corr().iloc[0, 1]
    print(f"  Correlation with Multidimensional Poverty (sdg1_2_mpi): {corr_mpi:.4f}")

if 'sdg7_1_ec' in df_clean.columns:
    corr_ec = df_clean[[target_var, 'sdg7_1_ec']].corr().iloc[0, 1]
    print(f"  Correlation with Electricity Coverage (sdg7_1_ec): {corr_ec:.4f}")

# 4. TRAIN/TEST SPLIT
print("\n[4/8] Splitting data...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
print(f"  ✓ Training set: {len(X_train)} provinces")
print(f"  ✓ Test set: {len(X_test)} provinces")

# 5. MODEL TRAINING WITH CROSS-VALIDATION
print("\n[5/8] Training Random Forest model...")
rf_model = RandomForestRegressor(
    n_estimators=500,
    max_depth=10,
    min_samples_split=5,
    min_samples_leaf=2,
    max_features='sqrt',
    random_state=42,
    n_jobs=-1,
    verbose=0
)

print("  Model configuration:")
print(f"    - n_estimators: {rf_model.n_estimators}")
print(f"    - max_depth: {rf_model.max_depth}")
print(f"    - min_samples_split: {rf_model.min_samples_split}")

print("\n  Performing 5-fold cross-validation...")
kfold = KFold(n_splits=5, shuffle=True, random_state=42)

cv_scores_r2 = cross_val_score(rf_model, X_train, y_train, cv=kfold, scoring='r2', n_jobs=-1)
cv_scores_mse = -cross_val_score(rf_model, X_train, y_train, cv=kfold, scoring='neg_mean_squared_error', n_jobs=-1)
cv_scores_mae = -cross_val_score(rf_model, X_train, y_train, cv=kfold, scoring='neg_mean_absolute_error', n_jobs=-1)

print(f"\n  Cross-Validation Results (5-Fold):")
print(f"    R² Score:  {cv_scores_r2.mean():.4f} (±{cv_scores_r2.std():.4f})")
print(f"    RMSE:      {np.sqrt(cv_scores_mse.mean()):.4f} (±{np.sqrt(cv_scores_mse.std()):.4f})")
print(f"    MAE:       {cv_scores_mae.mean():.4f} (±{cv_scores_mae.std():.4f})")

print("\n  Training final model on full training set...")
rf_model.fit(X_train, y_train)
print("  ✓ Model training complete!")

# 6. MODEL EVALUATION
print("\n[6/8] Evaluating model performance...")
y_train_pred = rf_model.predict(X_train)
y_test_pred = rf_model.predict(X_test)

train_r2 = r2_score(y_train, y_train_pred)
test_r2 = r2_score(y_test, y_test_pred)
train_rmse = np.sqrt(mean_squared_error(y_train, y_train_pred))
test_rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))
train_mae = mean_absolute_error(y_train, y_train_pred)
test_mae = mean_absolute_error(y_test, y_test_pred)

print(f"\n  Training Set Performance:")
print(f"    R² Score:  {train_r2:.4f}")
print(f"    RMSE:      {train_rmse:.4f}%")
print(f"    MAE:       {train_mae:.4f}%")

print(f"\n  Test Set Performance:")
print(f"    R² Score:  {test_r2:.4f}")
print(f"    RMSE:      {test_rmse:.4f}%")
print(f"    MAE:       {test_mae:.4f}%")

print(f"\n  Generalization Check:")
print(f"    R² Difference: {train_r2 - test_r2:.4f}")
if (train_r2 - test_r2) < 0.1:
    print("    ✓ Model shows good generalization")
else:
    print("    ⚠ Model may be overfitting")

# Interpretation of errors in real-world terms
print(f"\n  Real-World Interpretation:")
print(f"    Average error: ±{test_mae:.1f} percentage points")
print(f"    If actual energy poverty is 70%, model predicts 70±{test_mae:.1f}%")

# 7. FEATURE IMPORTANCE ANALYSIS
print("\n[7/8] Analyzing feature importance...")
feature_importance = pd.DataFrame({
    'feature': embedding_cols,
    'importance': rf_model.feature_importances_
}).sort_values('importance', ascending=False)

print(f"\n  Top 20 Most Important Features:")
print(feature_importance.head(20).to_string(index=False))

# Cumulative importance
feature_importance['cumulative_importance'] = feature_importance['importance'].cumsum()
n_features_80 = (feature_importance['cumulative_importance'] <= 0.80).sum() + 1
n_features_95 = (feature_importance['cumulative_importance'] <= 0.95).sum() + 1

print(f"\n  Cumulative Importance Analysis:")
print(f"    Features needed for 80% importance: {n_features_80} ({n_features_80/len(embedding_cols)*100:.1f}%)")
print(f"    Features needed for 95% importance: {n_features_95} ({n_features_95/len(embedding_cols)*100:.1f}%)")

# 8. PREDICTION ANALYSIS
print("\n[8/8] Analyzing predictions...")
y_pred_all = rf_model.predict(X)
results_df = df_clean[['prov_id', 'prov', 'dep', target_var]].copy()
results_df['predicted_eepr'] = y_pred_all
results_df['residual'] = results_df[target_var] - results_df['predicted_eepr']
results_df['abs_error'] = np.abs(results_df['residual'])

print(f"\n  Provinces with Largest Prediction Errors:")
print(f"\n  Top 5 Overpredictions (Model predicts MORE energy poverty than actual):")
overpred = results_df.nsmallest(5, 'residual')[[
    'prov', 'dep', target_var, 'predicted_eepr', 'residual'
]]
for idx, row in overpred.iterrows():
    print(f"    {row['prov']:30s} ({row['dep']:15s}): Actual={row[target_var]:.1f}%, Pred={row['predicted_eepr']:.1f}%, Diff={row['residual']:.1f}pp")

print(f"\n  Top 5 Underpredictions (Model predicts LESS energy poverty than actual):")
underpred = results_df.nlargest(5, 'residual')[[
    'prov', 'dep', target_var, 'predicted_eepr', 'residual'
]]
for idx, row in underpred.iterrows():
    print(f"    {row['prov']:30s} ({row['dep']:15s}): Actual={row[target_var]:.1f}%, Pred={row['predicted_eepr']:.1f}%, Diff={row['residual']:.1f}pp")

# Identify extreme cases
print(f"\n  Provinces with Highest Extreme Energy Poverty:")
highest = results_df.nlargest(5, target_var)[['prov', 'dep', target_var, 'predicted_eepr']]
for idx, row in highest.iterrows():
    print(f"    {row['prov']:30s} ({row['dep']:15s}): {row[target_var]:.1f}% (predicted: {row['predicted_eepr']:.1f}%)")

print(f"\n  Provinces with Lowest Extreme Energy Poverty:")
lowest = results_df.nsmallest(5, target_var)[['prov', 'dep', target_var, 'predicted_eepr']]
for idx, row in lowest.iterrows():
    print(f"    {row['prov']:30s} ({row['dep']:15s}): {row[target_var]:.1f}% (predicted: {row['predicted_eepr']:.1f}%)")

# SUMMARY
print("\n" + "="*80)
print("MODEL SUMMARY")
print("="*80)

print("\n📊 PERFORMANCE METRICS:")
print(f"  Cross-Validation R² (5-fold): {cv_scores_r2.mean():.4f} (±{cv_scores_r2.std():.4f})")
print(f"  Test Set R²:                  {test_r2:.4f}")
print(f"  Test Set RMSE:                {test_rmse:.4f}%")
print(f"  Test Set MAE:                 {test_mae:.4f}%")

print("\n🌟 FEATURE IMPORTANCE:")
print(f"  Total embedding dimensions:   {len(embedding_cols)}")
print(f"  Features for 80% importance:  {n_features_80} ({n_features_80/len(embedding_cols)*100:.1f}%)")
print(f"  Features for 95% importance:  {n_features_95} ({n_features_95/len(embedding_cols)*100:.1f}%)")
top_5_features = feature_importance.head(5)['feature'].tolist()
print(f"  Top 5 Features: {', '.join(top_5_features)}")

print("\n🎯 KEY INSIGHTS:")
if test_r2 > 0.7:
    print("  ✓ Strong predictive power: Satellite embeddings capture energy poverty patterns well")
elif test_r2 > 0.5:
    print("  ✓ Moderate predictive power: Satellite embeddings provide useful energy poverty signals")
elif test_r2 > 0.3:
    print("  ✓ Fair predictive power: Satellite embeddings show some relationship with energy poverty")
else:
    print("  ⚠ Limited predictive power: Additional features may be needed")

if (train_r2 - test_r2) < 0.1:
    print("  ✓ Good generalization: Model performs consistently on unseen data")
else:
    print("  ⚠ Potential overfitting: Consider regularization or ensemble approaches")

print("\n💡 RECOMMENDATIONS:")
print("  1. Extreme energy poverty is directly measured (% of houses), not a composite index")
print("  2. Night-time lights would provide direct evidence of electricity access/usage")
print("  3. Consider combining with:")
print("     - Electricity coverage data (sdg7_1_ec)")
print("     - Clean cooking energy (sdg7_1_cce)")
print("     - Infrastructure proximity (roads, power grid)")
print("  4. Geographic features like altitude and remoteness may be key predictors")
print("  5. Temporal analysis could track electrification progress over time")

print("\n📝 VARIABLE DEFINITION:")
print(f"  {target_var}: Extreme energy poverty rate, 2016")
print(f"  Definition: Percentage of houses in extreme energy poverty")
print(f"  Range in dataset: {y.min():.1f}% to {y.max():.1f}%")
print(f"  Mean: {y.mean():.1f}%")

print("\n" + "="*80)
print("Analysis complete! ✓")
print("="*80)
