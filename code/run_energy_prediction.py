#!/usr/bin/env python3
"""
Random Forest Model to Predict SDG 7 (Affordable Energy) using Satellite Embeddings
bolivia112 Project (province level)

NOTE: The unit of analysis is the 112 Bolivian provinces (not 339 municipalities).
This is a small sample for machine learning, so model performance, cross-validation
scores and feature importance should be interpreted with caution. All province
values are population-weighted aggregations of the municipal data (intensive
variables = weighted mean, extensive variables = sum). See the aggregation
methodology in ../province_aggregation_report.md.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score, KFold, train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import warnings
warnings.filterwarnings('ignore')

print("="*80)
print("RANDOM FOREST MODEL: SDG 7 ENERGY POVERTY PREDICTION")
print("bolivia112 - Predicting Energy Access from Satellite Embeddings")
print("="*80)

# Define repository URL
REPO_URL = "https://raw.githubusercontent.com/quarcs-lab/bolivia112/main"

# 1. LOAD DATASETS
print("\n[1/8] Loading datasets...")
url_names = f"{REPO_URL}/regionNames/regionNames.csv"
url_sdg = f"{REPO_URL}/sdg/sdg.csv"
url_embeddings = f"{REPO_URL}/satelliteEmbeddings/satelliteEmbeddings2017.csv"

df_names = pd.read_csv(url_names)
df_sdg = pd.read_csv(url_sdg)
df_embeddings = pd.read_csv(url_embeddings)

print(f"  ✓ Loaded {len(df_names)} provinces")
print(f"  ✓ Loaded {len(df_sdg.columns)-1} SDG variables")
print(f"  ✓ Loaded {len(df_embeddings.columns)-1} satellite embedding dimensions")

# 2. DATA PREPARATION
print("\n[2/8] Preparing data...")
df = pd.merge(df_names, df_sdg, on='prov_id', how='inner')
df = pd.merge(df, df_embeddings, on='prov_id', how='inner')

embedding_cols = [col for col in df.columns if col.startswith('A')]
df_clean = df[['prov_id', 'prov', 'dep', 'index_sdg7', 'index_sdg1'] + embedding_cols].dropna()

X = df_clean[embedding_cols].values
y = df_clean['index_sdg7'].values

print(f"  ✓ Final dataset shape: {df_clean.shape}")
print(f"  ✓ Features: {X.shape[1]} satellite embeddings")
print(f"  ✓ Target: SDG 7 Index (Affordable Energy)")
print(f"  ✓ Target range: {y.min():.2f} - {y.max():.2f} (mean: {y.mean():.2f})")

# 3. COMPARE WITH SDG 1 (POVERTY)
print("\n[3/8] Comparing Energy Poverty (SDG 7) vs General Poverty (SDG 1)...")
corr_sdg1_sdg7 = df_clean[['index_sdg1', 'index_sdg7']].corr().iloc[0, 1]
print(f"  Correlation between SDG 1 and SDG 7: {corr_sdg1_sdg7:.4f}")

if corr_sdg1_sdg7 > 0.7:
    print("  ✓ Strong positive correlation: Energy and general poverty are closely linked")
elif corr_sdg1_sdg7 > 0.4:
    print("  ✓ Moderate correlation: Energy and general poverty show some relationship")
else:
    print("  ⚠ Weak correlation: Energy and general poverty have distinct patterns")

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
print(f"    RMSE:      {train_rmse:.4f}")
print(f"    MAE:       {train_mae:.4f}")

print(f"\n  Test Set Performance:")
print(f"    R² Score:  {test_r2:.4f}")
print(f"    RMSE:      {test_rmse:.4f}")
print(f"    MAE:       {test_mae:.4f}")

print(f"\n  Generalization Check:")
print(f"    R² Difference: {train_r2 - test_r2:.4f}")
if (train_r2 - test_r2) < 0.1:
    print("    ✓ Model shows good generalization")
else:
    print("    ⚠ Model may be overfitting")

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
results_df = df_clean[['prov_id', 'prov', 'dep', 'index_sdg7', 'index_sdg1']].copy()
results_df['predicted_sdg7'] = y_pred_all
results_df['residual'] = results_df['index_sdg7'] - results_df['predicted_sdg7']
results_df['abs_error'] = np.abs(results_df['residual'])

print(f"\n  Provinces with Largest Prediction Errors:")
print(f"\n  Top 5 Overpredictions (Model predicts HIGHER than actual):")
overpred = results_df.nsmallest(5, 'residual')[['prov', 'dep', 'index_sdg7', 'predicted_sdg7', 'residual']]
for idx, row in overpred.iterrows():
    print(f"    {row['prov']:30s} ({row['dep']:15s}): Actual={row['index_sdg7']:.2f}, Pred={row['predicted_sdg7']:.2f}, Diff={row['residual']:.2f}")

print(f"\n  Top 5 Underpredictions (Model predicts LOWER than actual):")
underpred = results_df.nlargest(5, 'residual')[['prov', 'dep', 'index_sdg7', 'predicted_sdg7', 'residual']]
for idx, row in underpred.iterrows():
    print(f"    {row['prov']:30s} ({row['dep']:15s}): Actual={row['index_sdg7']:.2f}, Pred={row['predicted_sdg7']:.2f}, Diff={row['residual']:.2f}")

# COMPARATIVE ANALYSIS
print("\n" + "="*80)
print("COMPARATIVE ANALYSIS: Energy Poverty vs General Poverty")
print("="*80)

# Compare provinces with high energy poverty but low general poverty
high_energy_low_poverty = results_df[
    (results_df['index_sdg7'] > results_df['index_sdg7'].median()) &
    (results_df['index_sdg1'] < results_df['index_sdg1'].median())
].sort_values('index_sdg7', ascending=False).head(5)

if len(high_energy_low_poverty) > 0:
    print("\n🔋 Provinces with Good Energy Access BUT High General Poverty:")
    for idx, row in high_energy_low_poverty.iterrows():
        print(f"  {row['prov']:30s} ({row['dep']:15s}): SDG7={row['index_sdg7']:.1f}, SDG1={row['index_sdg1']:.1f}")
else:
    print("\n🔋 No provinces found with this pattern")

# Compare provinces with low energy poverty but high general poverty
low_energy_high_poverty = results_df[
    (results_df['index_sdg7'] < results_df['index_sdg7'].median()) &
    (results_df['index_sdg1'] > results_df['index_sdg1'].median())
].sort_values('index_sdg1', ascending=False).head(5)

if len(low_energy_high_poverty) > 0:
    print("\n⚡ Provinces with Poor Energy Access BUT Low General Poverty:")
    for idx, row in low_energy_high_poverty.iterrows():
        print(f"  {row['prov']:30s} ({row['dep']:15s}): SDG7={row['index_sdg7']:.1f}, SDG1={row['index_sdg1']:.1f}")
else:
    print("\n⚡ No provinces found with this pattern")

# SUMMARY
print("\n" + "="*80)
print("MODEL SUMMARY")
print("="*80)

print("\n📊 PERFORMANCE METRICS:")
print(f"  Cross-Validation R² (5-fold): {cv_scores_r2.mean():.4f} (±{cv_scores_r2.std():.4f})")
print(f"  Test Set R²:                  {test_r2:.4f}")
print(f"  Test Set RMSE:                {test_rmse:.4f}")
print(f"  Test Set MAE:                 {test_mae:.4f}")

print("\n🌟 FEATURE IMPORTANCE:")
print(f"  Total embedding dimensions:   {len(embedding_cols)}")
print(f"  Features for 80% importance:  {n_features_80} ({n_features_80/len(embedding_cols)*100:.1f}%)")
print(f"  Features for 95% importance:  {n_features_95} ({n_features_95/len(embedding_cols)*100:.1f}%)")
top_5_features = feature_importance.head(5)['feature'].tolist()
print(f"  Top 5 Features: {', '.join(top_5_features)}")

print("\n🔗 RELATIONSHIP WITH POVERTY:")
print(f"  Correlation SDG 1 vs SDG 7:   {corr_sdg1_sdg7:.4f}")

print("\n🎯 KEY INSIGHTS:")
if test_r2 > 0.7:
    print("  ✓ Strong predictive power: Satellite embeddings capture energy poverty patterns well")
elif test_r2 > 0.5:
    print("  ✓ Moderate predictive power: Satellite embeddings provide useful energy poverty signals")
else:
    print("  ⚠ Limited predictive power: Additional features may be needed")

if (train_r2 - test_r2) < 0.1:
    print("  ✓ Good generalization: Model performs consistently on unseen data")
else:
    print("  ⚠ Potential overfitting: Consider regularization or ensemble approaches")

print("\n💡 RECOMMENDATIONS:")
print("  1. Energy poverty shows distinct spatial patterns requiring targeted interventions")
print("  2. Night-time lights (NTL) data would be highly complementary for energy access")
print("  3. Combine with infrastructure data (roads, power lines) for better predictions")
print("  4. Urban areas may have different energy access patterns than rural regions")
print("  5. Temporal analysis could reveal electrification and renewable energy trends")
print("  6. Consider SDG 9 (Infrastructure) as an intermediate predictor variable")

print("\n" + "="*80)
print("Analysis complete! ✓")
print("="*80)
