import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score, KFold
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import warnings
warnings.filterwarnings('ignore')
import os # Import the os module

# NOTE: The unit of analysis is the 112 Bolivian provinces (not 339 municipalities).
# This is a SMALL sample for machine learning, so model performance and feature
# importance estimates are less stable than at the municipal level. All province
# values are POPULATION-WEIGHTED AGGREGATIONS of the underlying municipal data
# (intensive variables = weighted mean, extensive variables = sum). See
# ../province_aggregation_report.md for details.

# Set random seed for reproducibility
RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)

print("="*80)
print("PREDICTING PROVINCIAL SUSTAINABLE DEVELOPMENT INDEX (IMDS)")
print("Using Satellite Embeddings from Google Earth Engine")
print("="*80)
print()

# Create the 'code' directory if it doesn't exist
output_dir = 'code'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"  ✓ Created output directory: {output_dir}/")
print()

# ==============================================================================
# 1. DATA LOADING
# ==============================================================================
print("[1/7] Loading datasets...")

# Load SDG data (contains IMDS)
url_sdg = "https://raw.githubusercontent.com/quarcs-lab/bolivia112/main/sdg/sdg.csv"
df_sdg = pd.read_csv(url_sdg)

# Load satellite embeddings
url_emb = "https://raw.githubusercontent.com/quarcs-lab/bolivia112/main/satelliteEmbeddings/satelliteEmbeddings2017.csv"
df_embeddings = pd.read_csv(url_emb)

# Load region names for interpretation
url_names = "https://raw.githubusercontent.com/quarcs-lab/bolivia112/main/regionNames/regionNames.csv"
df_names = pd.read_csv(url_names)

print(f"  ✓ SDG data loaded: {len(df_sdg)} provinces")
print(f"  ✓ Satellite embeddings loaded: {len(df_embeddings)} provinces")
print(f"  ✓ Region names loaded: {len(df_names)} provinces")
print()

# ==============================================================================
# 2. DATA PREPARATION
# ==============================================================================
print("[2/7] Preparing data...")

# Merge datasets
df_merged = df_sdg[['prov_id', 'imds']].merge(
    df_embeddings,
    on='prov_id',
    how='inner'
)
df_merged = df_merged.merge(
    df_names[['prov_id', 'prov', 'dep']],
    on='prov_id',
    how='left'
)

# Check for missing values in IMDS
missing_imds = df_merged['imds'].isna().sum()
print(f"  • Missing IMDS values: {missing_imds}")

# Remove rows with missing IMDS
df_clean = df_merged.dropna(subset=['imds']).copy()
print(f"  • Valid provinces for analysis: {len(df_clean)}")

# Prepare features (X) and target (y)
embedding_cols = [f'A{str(i).zfill(2)}' for i in range(64)]
X = df_clean[embedding_cols].values
y = df_clean['imds'].values

print(f"  • Feature matrix shape: {X.shape}")
print(f"  • Target variable shape: {y.shape}")
print(f"  • IMDS range: [{y.min():.2f}, {y.max():.2f}]")
print(f"  • IMDS mean: {y.mean():.2f} ± {y.std():.2f}")
print()

# ==============================================================================
# 3. TRAIN-TEST SPLIT
# ==============================================================================
print("[3/7] Splitting data into train and test sets...")

X_train, X_test, y_train, y_test, idx_train, idx_test = train_test_split(
    X, y, df_clean.index,
    test_size=0.2,
    random_state=RANDOM_STATE
)

print(f"  • Training set: {len(X_train)} provinces")
print(f"  • Test set: {len(X_test)} provinces")
print()

# ==============================================================================
# 4. MODEL CONFIGURATION
# ==============================================================================
print("[4/7] Configuring Random Forest model...")
print("  Using standard hyperparameters (memory-efficient)...")
print()

# Use standard hyperparameters - lighter for memory
best_params = {
    'n_estimators': 100,        # Reduced from 500 for memory
    'max_depth': 20,            # Limited depth to prevent overfitting
    'min_samples_split': 5,
    'min_samples_leaf': 2,
    'max_features': 'sqrt',
    'random_state': RANDOM_STATE,
    'n_jobs': 1                 # Single thread to save memory
}

print("  Hyperparameters:")
for param, value in best_params.items():
    if param not in ['random_state', 'n_jobs']:
        print(f"    • {param}: {value}")
print()

# ==============================================================================
# 5. CROSS-VALIDATION
# ==============================================================================
print("[5/7] Performing 5-fold cross-validation...")

# Initialize model
rf_model = RandomForestRegressor(**best_params)

# Setup cross-validation
cv = KFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)

# Perform cross-validation (sequential, not parallel)
cv_scores = cross_val_score(rf_model, X_train, y_train, cv=cv, scoring='r2', n_jobs=1)

print(f"  • Cross-validation R² scores: {[f'{s:.4f}' for s in cv_scores]}")
print(f"  • Mean CV R²: {cv_scores.mean():.4f} (±{cv_scores.std():.4f})")
print()

# ==============================================================================
# 6. MODEL TRAINING AND EVALUATION
# ==============================================================================
print("[6/7] Training final model and evaluating...")

# Train on full training set
rf_model.fit(X_train, y_train)
print("  ✓ Training complete")

# Predictions
y_train_pred = rf_model.predict(X_train)
y_test_pred = rf_model.predict(X_test)

# Training metrics
train_r2 = r2_score(y_train, y_train_pred)
train_rmse = np.sqrt(mean_squared_error(y_train, y_train_pred))
train_mae = mean_absolute_error(y_train, y_train_pred)

# Test metrics
test_r2 = r2_score(y_test, y_test_pred)
test_rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))
test_mae = mean_absolute_error(y_test, y_test_pred)

print()
print("  PERFORMANCE METRICS:")
print("  " + "-"*50)
print(f"  Training Set:")
print(f"    • R² Score:  {train_r2:.4f}")
print(f"    • RMSE:      {train_rmse:.4f}")
print(f"    • MAE:       {train_mae:.4f}")
print()
print(f"  Test Set:")
print(f"    • R² Score:  {test_r2:.4f}")
print(f"    • RMSE:      {test_rmse:.4f}")
print(f"    • MAE:       {test_mae:.4f}")
print("  " + "-"*50)
print()

# Calculate prediction errors
test_errors = y_test - y_test_pred

# ==============================================================================
# 7. FEATURE IMPORTANCE ANALYSIS
# ==============================================================================
print("[7/7] Analyzing feature importance...")

# Get feature importances from the model
importances = rf_model.feature_importances_
indices = np.argsort(importances)[::-1]

print()
print("  TOP 20 MOST IMPORTANT FEATURES:")
print("  " + "-"*60)
print(f"  {'Rank':<6} {'Feature':<10} {'Importance':<12} {'Cumulative %'}")
print("  " + "-"*60)

cumulative_importance = 0
for i in range(20):
    idx = indices[i]
    cumulative_importance += importances[idx]
    print(f"  {i+1:<6} {embedding_cols[idx]:<10} {importances[idx]:.6f}     {cumulative_importance*100:.2f}%")

print("  " + "-"*60)
print()

# Calculate how many features needed for 80% importance
cumsum = np.cumsum(importances[indices])
n_features_80 = np.argmax(cumsum >= 0.80) + 1
print(f"  • Features needed for 80% importance: {n_features_80}/64 ({n_features_80/64*100:.1f}%)")
print()

# ==============================================================================
# 8. IDENTIFY PROVINCES WITH LARGEST ERRORS
# ==============================================================================
print("PROVINCES WITH LARGEST PREDICTION ERRORS:")
print("="*80)

# Create results dataframe for test set
test_results = df_clean.iloc[idx_test].copy()
test_results['imds_actual'] = y_test
test_results['imds_predicted'] = y_test_pred
test_results['error'] = test_errors
test_results['abs_error'] = np.abs(test_errors)

# Top 10 overpredicted (model predicts higher than actual)
overpredicted = test_results.nsmallest(10, 'error')
print()
print("Top 10 OVERPREDICTED (Model predicts higher development than actual):")
print("-"*80)
for _, row in overpredicted.iterrows():
    print(f"  {row['prov']}, {row['dep']}")
    print(f"    Actual: {row['imds_actual']:.2f} | Predicted: {row['imds_predicted']:.2f} | Error: {row['error']:.2f}")

# Top 10 underpredicted (model predicts lower than actual)
underpredicted = test_results.nlargest(10, 'error')
print()
print("Top 10 UNDERPREDICTED (Model predicts lower development than actual):")
print("-"*80)
for _, row in underpredicted.iterrows():
    print(f"  {row['prov']}, {row['dep']}")
    print(f"    Actual: {row['imds_actual']:.2f} | Predicted: {row['imds_predicted']:.2f} | Error: {row['error']:.2f}")

print()
print("="*80)

# ==============================================================================
# 9. VISUALIZATIONS
# ==============================================================================
print()
print("Generating visualizations...")

# Create figure with subplots
fig = plt.figure(figsize=(16, 12))

# 1. Actual vs Predicted
ax1 = plt.subplot(2, 3, 1)
ax1.scatter(y_test, y_test_pred, alpha=0.6, edgecolors='k', linewidth=0.5)
ax1.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
ax1.set_xlabel('Actual IMDS', fontsize=11)
ax1.set_ylabel('Predicted IMDS', fontsize=11)
ax1.set_title(f'Actual vs Predicted IMDS\nTest R² = {test_r2:.4f}', fontsize=12, fontweight='bold')
ax1.grid(True, alpha=0.3)

# 2. Residual plot
ax2 = plt.subplot(2, 3, 2)
ax2.scatter(y_test_pred, test_errors, alpha=0.6, edgecolors='k', linewidth=0.5)
ax2.axhline(y=0, color='r', linestyle='--', lw=2)
ax2.set_xlabel('Predicted IMDS', fontsize=11)
ax2.set_ylabel('Residuals (Actual - Predicted)', fontsize=11)
ax2.set_title('Residual Plot', fontsize=12, fontweight='bold')
ax2.grid(True, alpha=0.3)

# 3. Error distribution
ax3 = plt.subplot(2, 3, 3)
ax3.hist(test_errors, bins=15, edgecolor='black', alpha=0.7)
ax3.axvline(x=0, color='r', linestyle='--', lw=2)
ax3.set_xlabel('Prediction Error', fontsize=11)
ax3.set_ylabel('Frequency', fontsize=11)
ax3.set_title(f'Distribution of Errors\nMAE = {test_mae:.2f}', fontsize=12, fontweight='bold')
ax3.grid(True, alpha=0.3, axis='y')

# 4. Feature importance
ax4 = plt.subplot(2, 3, 4)
top_n = 20
top_indices = indices[:top_n]
top_features = [embedding_cols[i] for i in top_indices]
top_importances = importances[top_indices]
ax4.barh(range(top_n), top_importances, edgecolor='black')
ax4.set_yticks(range(top_n))
ax4.set_yticklabels(top_features, fontsize=9)
ax4.set_xlabel('Importance', fontsize=11)
ax4.set_title('Top 20 Feature Importances', fontsize=12, fontweight='bold')
ax4.invert_yaxis()
ax4.grid(True, alpha=0.3, axis='x')

# 5. Cumulative importance
ax5 = plt.subplot(2, 3, 5)
ax5.plot(range(1, 65), cumsum, linewidth=2, marker='o', markersize=3)
ax5.axhline(y=0.8, color='r', linestyle='--', lw=2, label='80% threshold')
ax5.axvline(x=n_features_80, color='g', linestyle='--', lw=2, label=f'{n_features_80} features')
ax5.set_xlabel('Number of Features', fontsize=11)
ax5.set_ylabel('Cumulative Importance', fontsize=11)
ax5.set_title('Cumulative Feature Importance', fontsize=12, fontweight='bold')
ax5.legend(fontsize=9)
ax5.grid(True, alpha=0.3)

# 6. Cross-validation scores
ax6 = plt.subplot(2, 3, 6)
ax6.bar(range(1, len(cv_scores)+1), cv_scores, edgecolor='black', alpha=0.7)
ax6.axhline(y=cv_scores.mean(), color='r', linestyle='--', lw=2, label=f'Mean: {cv_scores.mean():.4f}')
ax6.set_xlabel('Fold', fontsize=11)
ax6.set_ylabel('R² Score', fontsize=11)
ax6.set_title('Cross-Validation R² Scores', fontsize=12, fontweight='bold')
ax6.set_xticks(range(1, len(cv_scores)+1))
ax6.legend(fontsize=9)
ax6.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('code/imds_prediction_results.png', dpi=150, bbox_inches='tight')
plt.close()
print("  ✓ Visualization saved: code/imds_prediction_results.png")

# ==============================================================================
# 10. SAVE DETAILED RESULTS
# ==============================================================================
print()
print("Saving detailed results...")

# Save all predictions for test set
test_results_sorted = test_results.sort_values('abs_error', ascending=False)
test_results_sorted.to_csv('code/imds_test_predictions.csv', index=False)
print("  ✓ Test predictions saved: code/imds_test_predictions.csv")

# Save feature importances
feature_importance_df = pd.DataFrame({
    'feature': embedding_cols,
    'importance': importances,
    'rank': np.argsort(np.argsort(importances)[::-1]) + 1
}).sort_values('importance', ascending=False)
feature_importance_df.to_csv('code/imds_feature_importance.csv', index=False)
print("  ✓ Feature importances saved: code/imds_feature_importance.csv")

# Save model summary
summary = {
    'Model': 'Random Forest Regressor',
    'Target Variable': 'IMDS (Provincial Sustainable Development Index)',
    'Number of Features': 64,
    'Training Samples': len(X_train),
    'Test Samples': len(X_test),
    'n_estimators': best_params['n_estimators'],
    'max_depth': best_params['max_depth'],
    'min_samples_split': best_params['min_samples_split'],
    'min_samples_leaf': best_params['min_samples_leaf'],
    'max_features': best_params['max_features'],
    'CV Mean R2': f"{cv_scores.mean():.4f}",
    'CV Std R2': f"{cv_scores.std():.4f}",
    'Test R2': f"{test_r2:.4f}",
    'Test RMSE': f"{test_rmse:.4f}",
    'Test MAE': f"{test_mae:.4f}",
    'Features for 80% Importance': n_features_80
}

summary_df = pd.DataFrame([summary]).T
summary_df.columns = ['Value']
summary_df.to_csv('code/imds_model_summary.csv')
print("  ✓ Model summary saved: code/imds_model_summary.csv")

print()
print("="*80)
print("ANALYSIS COMPLETE!")
print("="*80)
print()
print("Key Findings:")
print(f"  • The model explains {test_r2*100:.2f}% of variance in IMDS")
print(f"  • Average prediction error: ±{test_mae:.2f} IMDS points")
print(f"  • Only {n_features_80} out of 64 features ({n_features_80/64*100:.1f}%) account for 80% of predictive power")
print(f"  • Cross-validation R²: {cv_scores.mean():.4f} (±{cv_scores.std():.4f})")
print()
print("Files generated:")
print("  1. imds_prediction_results.png - Comprehensive visualization")
print("  2. imds_test_predictions.csv - Detailed predictions for test set")
print("  3. imds_feature_importance.csv - Feature importance rankings")
print("  4. imds_model_summary.csv - Model configuration and performance")
print()