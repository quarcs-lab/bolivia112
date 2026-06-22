# Working with Claude on bolivia112

This guide helps you effectively collaborate with Claude (AI assistant) on the bolivia112 project. Whether you're analyzing data, creating visualizations, or extending the repository, these practices will help you get the best results.

> **About this dataset**: bolivia112 is the population-weighted province-level aggregation of [DS4Bolivia](https://github.com/quarcs-lab/ds4bolivia). The 339 municipalities are aggregated into 112 provinces — intensive variables use population-weighted means and extensive variables are summed. See [`../province_aggregation_report.md`](../province_aggregation_report.md) for the full aggregation methodology.

## Quick Start Prompts

### Data Analysis
```
"Load the SDG indices and satellite embeddings for province X and create
a correlation analysis between poverty indicators and night-time lights."
```

### Spatial Analysis
```
"Create a choropleth map showing SDG 3 (Good Health) across all provinces,
highlighting spatial clusters using Local Moran's I."
```

### Machine Learning
```
"Build a random forest model to predict SDG 1 (No Poverty) using the satellite
embeddings as features. Include feature importance analysis."
```

## Project Structure Overview

When working with Claude, reference these key directories:

- **`/regionNames/`** - Administrative metadata (province names, IDs)
- **`/sdg/`** - 15 composite SDG indices
- **`/sdgVariables/`** - 64 granular SDG indicators
- **`/pop/`** - Population time series (2001-2020)
- **`/ntl/`** - Night-time lights data (2012-2020)
- **`/satelliteEmbeddings/`** - 64-dimensional satellite imagery features
- **`/datasets/`** - Pre-merged datasets ready for ML
- **`/gdp/`** - GDP per capita time series (1990-2024)
- **`/maps/`** - GeoJSON boundaries for 112 provinces
- **`/notebooks/`** - Jupyter tutorials and examples
- **`/code/`** - Data processing scripts (Stata, Python, JavaScript/GEE)
- **`/apps/`** - Interactive web applications

## Environment Setup (UV)

This project uses [UV](https://docs.astral.sh/uv/) for Python package management. All dependencies are declared in `pyproject.toml` and pinned in `uv.lock`.

### Key Commands

```bash
# Install all dependencies (first time or after pulling changes)
uv sync

# Run a Python script
uv run python code/run_poverty_prediction.py

# Launch Jupyter notebooks
uv run jupyter notebook

# Add a new dependency
uv add <package-name>

# Update all dependencies
uv lock --upgrade && uv sync
```

### Important Notes

- **Always use `uv run`** to execute Python scripts and Jupyter. This ensures the correct virtual environment is used.
- **Commit `uv.lock`** after adding or updating dependencies. This file ensures reproducible builds.
- **Do not commit `.venv/`** — it is in `.gitignore`.
- **Google Colab compatibility**: Notebooks include `!pip install` cells for packages not in Colab's default environment. These cells are harmless when running locally with UV since the packages are already installed.
- When suggesting code to users, prefer `uv run python script.py` over `python script.py`.

## Key Identifiers

**Always use `prov_id` as the primary join key** when merging datasets. This is the 3-digit INE province code (e.g. `405` = Litoral) and ensures consistency across all files, especially satellite embeddings and optimized maps.

```python
# ✅ Correct
df_merged = pd.merge(df_sdg, df_satellite, on='prov_id', how='inner')

# ⚠️ Note: municipal-only ids (asdf_id, mun_id, poly_id, shapeID, dep_mun) do NOT exist
# in the province tables — always join on prov_id.
```

## Common Tasks

### 1. Loading and Merging Data

**Prompt Template:**
```
"Load the [dataset1] and [dataset2] from the repository, merge them on prov_id,
and show me the first few rows with columns [specific columns]."
```

**Example:**
```
"Load the SDG indices and population data, merge them, and calculate the
correlation between SDG 1 (No Poverty) and population density for 2020."
```

### 2. Spatial Visualization

**Prompt Template:**
```
"Create a map of [variable name] using the GeoJSON boundaries. Use a
[color scheme] colormap and highlight [specific provinces/patterns]."
```

**Example:**
```
"Create a choropleth map of index_sdg8 (Decent Work) with a viridis colormap.
Add province boundaries and identify the top 10 performing provinces."
```

### 3. Exploratory Spatial Data Analysis (ESDA)

**Prompt Template:**
```
"Perform ESDA on [variable] using [method: Global Moran's I / Local Moran's I /
LISA clusters]. Visualize the results with appropriate maps."
```

**Example:**
```
"Calculate Local Moran's I for night-time lights in 2019. Create a LISA cluster
map showing High-High, Low-Low, High-Low, and Low-High clusters."
```

### 4. Machine Learning with Satellite Data

**Prompt Template:**
```
"Build a [model type] to predict [target variable] using satellite embeddings.
Include [validation method] and visualize [specific outputs]."
```

**Example:**
```
"Build a gradient boosting model to predict index_sdg1 using the 2017 satellite
embeddings. Use 5-fold cross-validation and show feature importance for the top
20 embedding dimensions."
```

### 5. Time Series Analysis

**Prompt Template:**
```
"Analyze the temporal trend of [variable] from [start year] to [end year].
Show [visualization type] and calculate [specific statistics]."
```

**Example:**
```
"Analyze population growth trends from 2001 to 2020 for departments with the
highest urbanization. Create line plots and calculate annual growth rates."
```

## Best Practices for Prompts

### Be Specific About Data Sources
```
✅ "Use the pre-merged dataset at /datasets/sdgs_satelliteEmbeddings2017.csv"
❌ "Use the data"
```

### Specify Output Format
```
✅ "Create a matplotlib figure with 2 subplots showing the distribution and
spatial pattern of SDG 10 (Reduced Inequalities)"
❌ "Show me SDG 10"
```

### Request Validation Steps
```
✅ "Merge the datasets, verify the number of rows matches 112 provinces,
and check for any missing values in key columns"
❌ "Merge the datasets"
```

### Ask for Interpretations
```
✅ "After creating the map, explain any visible spatial patterns and suggest
potential factors driving regional disparities"
❌ "Create a map"
```

## Working with Notebooks

When asking Claude to work with or create Jupyter notebooks:

```
"Create a Jupyter notebook that:
1. Loads the SDG and satellite data
2. Performs dimensionality reduction (PCA) on the embeddings
3. Creates a scatter plot colored by SDG 1 index
4. Includes markdown explanations for each step
5. Is ready to run in Google Colab"
```

## Debugging and Troubleshooting

### Data Type Issues
```
"I'm getting a merge error with prov_id. Check the data types in both dataframes
and convert them to integers if needed before merging."
```

### Missing Data
```
"Analyze missing values in the merged dataset. Show the percentage of missing
values per column and suggest imputation strategies for [specific variable]."
```

### Spatial Data Problems
```
"The GeoJSON isn't loading correctly. Verify the file path, check the CRS,
and ensure prov_id is properly formatted as integer."
```

## Advanced Analysis Examples

### Multi-Scale Spatial Analysis
```
"Perform spatial analysis at both province and department levels. Aggregate
the data by department, compare spatial autocorrelation patterns, and identify
scale-dependent effects on SDG 7 (Affordable Energy)."
```

### Predictive Mapping
```
"Train a model using provinces with SDG data and satellite embeddings.
Then create predictions for any provinces missing SDG data. Visualize
both observed and predicted values on a map with confidence intervals."
```

### Comparative Analysis
```
"Compare the spatial distribution of SDG 1 (No Poverty) with night-time lights
intensity. Calculate spatial correlation, create bivariate maps, and identify
provinces where poverty levels don't match expected patterns based on NTL."
```

## Code Style Preferences

When asking Claude to write code for this project:

- **Use pandas** for tabular data manipulation
- **Use geopandas** for spatial operations
- **Use matplotlib/seaborn** for static visualizations
- **Use folium** for interactive maps
- **Use scikit-learn** for machine learning
- **Use PySAL** for spatial statistics

### Example Style Request
```
"Write the analysis using pandas and geopandas. Include clear comments,
use descriptive variable names, and structure the code in logical sections
with markdown headers if creating a notebook."
```

## Documentation Requests

### Create Analysis Documentation
```
"Document the analysis we just performed in markdown format. Include:
- Objective and research question
- Data sources used (with file paths)
- Methods applied
- Key findings with supporting visualizations
- Limitations and caveats
- Suggestions for further analysis"
```

### Generate Variable Descriptions
```
"Create a data dictionary for the merged dataset showing variable names,
descriptions, data types, units, and valid ranges."
```

## Reproducibility Tips

When working on analysis that should be reproducible:

```
"Create a complete workflow that:
1. Uses only raw data from the repository (provide URLs)
2. Includes all data processing steps
3. Sets random seeds for any stochastic operations
4. Saves intermediate results to CSV
5. Generates publication-ready figures
6. Runs in Google Colab without local dependencies"
```

## Contributing New Features

When developing new features for the repository:

```
"I want to add [new dataset/feature]. Help me:
1. Determine the appropriate directory structure
2. Create a README following the existing format
3. Ensure the data uses prov_id as the join key
4. Add a usage example similar to existing documentation
5. Update the main README with references to the new data"
```

## Citation and Attribution

When Claude helps with analysis that leads to research outputs:

```
"Generate appropriate citations for:
1. The bolivia112 repository (following the format in README.md)
2. The original SDG data source
3. Any Python libraries used in the analysis
4. Any methodological references for spatial statistics applied"
```

## Getting Help

If Claude's responses aren't meeting your needs:

1. **Provide more context**: Share the specific research question or goal
2. **Show examples**: Reference similar analyses in the `/notebooks/` directory
3. **Specify constraints**: Mention computational limits, time constraints, or output requirements
4. **Request alternatives**: Ask for multiple approaches to compare
5. **Iterate**: Refine the analysis step-by-step rather than requesting everything at once

## Example Workflow

Here's a complete example of working with Claude on a research question:

```markdown
**Initial Request:**
"I want to investigate whether satellite-derived features can predict
multidimensional poverty (SDG 1) better than night-time lights alone."

**Follow-up 1:**
"Load the necessary datasets: SDG indices, satellite embeddings 2017,
and night-time lights for 2017."

**Follow-up 2:**
"Create three models: (1) NTL only, (2) satellite embeddings only,
(3) both combined. Use random forest with cross-validation."

**Follow-up 3:**
"Compare model performance using R², RMSE, and MAE. Create a visualization
showing predicted vs actual values for each model."

**Follow-up 4:**
"Generate a map showing where each model performs best. Identify systematic
patterns in prediction errors."

**Follow-up 5:**
"Summarize the findings in a format suitable for a research paper, including
a methods section and discussion of limitations."
```

## Resources

- **Main README**: [/README.md](README.md) - Overview and getting started
- **Dataset Documentation**: Each dataset folder has a detailed README
- **Example Notebook**: [/notebooks/esda.ipynb](notebooks/esda.ipynb) - ESDA tutorial
- **GitHub Repository**: https://github.com/quarcs-lab/bolivia112

---

**Pro Tip**: Start simple and iterate. Begin with basic data exploration, then progressively add complexity to your analysis. Claude can help at every step, from initial data loading to final publication-ready visualizations.
