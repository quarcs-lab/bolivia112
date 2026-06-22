# Sustainable Development Goals (SDG) Indices

## Overview

This directory contains composite indices measuring progress toward the United Nations Sustainable Development Goals (SDGs) for Bolivia's 112 provinces. These indices provide a comprehensive view of social, economic, and environmental development at the provincial level.

> **Note:** Province values are population-weighted aggregations of the underlying municipal data (intensive variables = weighted mean, extensive variables = sum). See [../province_aggregation_report.md](../province_aggregation_report.md).

## Files

### sdg.csv

Contains aggregated SDG indices for all 17 goals tracked in Bolivia.

## Variable Dictionary

| Variable Name | Description |
| --- | --- |
| **prov_id** | Unique province identifier (3-digit INE code) for joining datasets |
| **imds** | Provincial Sustainable Development Index (IMDS): Composite index aggregating all SDG indicators into a single provincial development score |
| **index_sdg1** | SDG 1 Index: No Poverty - Measures poverty rates, basic needs coverage, and economic security |
| **index_sdg2** | SDG 2 Index: Zero Hunger - Tracks malnutrition, food security, and agricultural productivity |
| **index_sdg3** | SDG 3 Index: Good Health and Well-being - Covers mortality rates, disease incidence, and healthcare access |
| **index_sdg4** | SDG 4 Index: Quality Education - Measures educational attainment, literacy, and school quality |
| **index_sdg5** | SDG 5 Index: Gender Equality - Tracks gender parity in education, employment, and decision-making |
| **index_sdg6** | SDG 6 Index: Clean Water and Sanitation - Measures access to drinking water, sanitation, and wastewater treatment |
| **index_sdg7** | SDG 7 Index: Affordable and Clean Energy - Covers electricity access, clean cooking fuels, and energy consumption |
| **index_sdg8** | SDG 8 Index: Decent Work and Economic Growth - Tracks employment, labor participation, and economic activity |
| **index_sdg9** | SDG 9 Index: Industry, Innovation and Infrastructure - Measures infrastructure, technology access, and connectivity |
| **index_sdg10** | SDG 10 Index: Reduced Inequalities - Tracks income inequality, education inequality, and social inclusion |
| **index_sdg11** | SDG 11 Index: Sustainable Cities and Communities - Covers housing quality, public transport, and urban planning |
| **index_sdg13** | SDG 13 Index: Climate Action - Measures climate vulnerability, emissions, and deforestation |
| **index_sdg15** | SDG 15 Index: Life on Land - Tracks protected areas, biodiversity, and ecosystem conservation |
| **index_sdg16** | SDG 16 Index: Peace, Justice and Strong Institutions - Measures safety, governance capacity, and civil registration |
| **index_sdg17** | SDG 17 Index: Partnerships for the Goals - Covers fiscal capacity, public investment, and resource mobilization |

## Index Scale

All indices are scaled from 0-100, where:
- **0** = Furthest from achieving the SDG target
- **100** = SDG target fully achieved

## Usage

This dataset is used for:

- **Development Monitoring**: Track provincial progress toward SDG targets
- **Spatial Analysis**: Identify geographic clusters of high/low SDG achievement
- **Policy Targeting**: Identify provinces requiring intervention
- **Correlation Studies**: Examine relationships between different SDGs
- **Machine Learning**: Use as target variables for predictive models with satellite data

## Example Code

You can run the examples below in [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/notebooks/empty.ipynb)

```python
import pandas as pd
import geopandas as gpd

# Load SDG indices
url = "https://raw.githubusercontent.com/quarcs-lab/bolivia112/main/sdg/sdg.csv"
df_sdg = pd.read_csv(url)

# Calculate average SDG achievement
sdg_cols = [f'index_sdg{i}' for i in [1,2,3,4,5,6,7,8,9,10,11,13,15,16,17]]
df_sdg['avg_sdg'] = df_sdg[sdg_cols].mean(axis=1)

# Identify provinces with low SDG achievement
low_sdg = df_sdg[df_sdg['avg_sdg'] < 50]
```

## Data Source

SDG indicators are originally constructed by:

**Andersen, L. E., Canelas, S., Gonzales, A., Peñaranda, L. (2020)**
*Atlas municipal de los Objetivos de Desarrollo Sostenible en Bolivia 2020*
La Paz: Universidad Privada Boliviana, SDSN Bolivia
Available at: [https://atlas.sdsnbolivia.org](https://atlas.sdsnbolivia.org)

## Detailed Variables

For detailed information on the underlying variables that compose these indices, see [sdgVariables/README.md](../sdgVariables/README.md).

## Join Key

Use `prov_id` to join this dataset with other datasets in the repository.
