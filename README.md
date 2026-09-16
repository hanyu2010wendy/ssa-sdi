# Sustainable Development Index for Sub-Saharan Africa

## Portfolio Summary

This project demonstrates my experience in international development data
analysis, including multi-source indicator compilation, country-year panel data
preparation, missing-data diagnostics, composite index construction, robustness
checks, and policy-oriented visualization for Sub-Saharan Africa.

It is relevant to roles in development data analysis, SDG monitoring, research
support, monitoring and evaluation, and higher-education planning/reporting.

## Skills Demonstrated

- International development indicators and SDG-related data
- Country-year panel data cleaning and harmonisation
- Indicator metadata and source documentation
- Missing-data diagnostics and transparency tables
- Composite index construction and robustness checks
- Python-based reproducible analysis and data visualization

## Portfolio Project

For a concise, job-facing example of SQL querying and policy-facing data
communication, see:

- [`portfolio/sql-sdi-analysis/`](portfolio/sql-sdi-analysis/): a small portfolio project using the final
  country-year SDI dataset to produce latest-year rankings, regional
  comparisons, and a country trend example.

This repository contains the processed data, indicator metadata, and replication
code for the manuscript:

**Subsystem divergence in sustainable development across Sub-Saharan Africa,
2001-2021: a composite indicator analysis**

The study constructs a subsystem-based sustainable development index (SDI) for
45 Sub-Saharan African countries from 2001 to 2021. The index separates
economic, social, resource, and ecological sustainability and applies a
two-stage CRITIC weighting procedure.

## Data Availability Statement

The processed data, indicator metadata, and replication code supporting the
findings of this study are available in this repository. Raw data were obtained
from publicly available international sources, including:

- World Bank World Development Indicators (WDI)
- Yale Environmental Performance Index (EPI)
- Food and Agriculture Organization (FAO)
- U.S. Energy Information Administration (EIA)
- IMF Climate Change Dashboard

## Key Data Files

- `index_data.csv`: final country-year SDI and subsystem scores.
- `index_data_two_stage_comparison.csv`: two-stage index scores used for
  comparisons and figures.
- `selected_indicator_system_variables.csv`: final indicator list.
- `indicator_system_summary.csv`: subsystem and sub-dimension summary.
- `critic_weight_two_stage.csv`: final two-stage CRITIC indicator weights.
- `appendix_missing_data_by_indicator.csv`: missingness and interpolation
  diagnostics by indicator.
- `appendix_missing_data_by_country.csv`: missingness and interpolation
  diagnostics by country.
- `sensitivity_weight_comparison.csv`: robustness comparison between the main
  two-stage CRITIC index and alternative weighting specifications.
- `sensitivity_equal_weight_table.csv`: equal-weight subsystem robustness
  results.

Excel versions of several tables are retained for manuscript preparation, but
the CSV files above are the main reproducibility files.

## Repository Layout

- `scripts/`: Python scripts for index reconstruction, missing-data summaries,
  robustness checks, tables, and figures.
- `notebooks/`: original exploratory and data-preparation notebooks.
- `figures/`: generated figures used in the manuscript.
- `output/indicator_change_analysis_2001_2021/`: generated indicator-change
  evidence tables and notes.
- Root-level `.csv` and `.xlsx` files: working inputs and generated outputs
  retained with their original filenames so the scripts remain reproducible.

## Environment

The project uses the conda environment recorded in `environment.yml`.

Create the environment:

```bash
conda env create -f environment.yml
conda activate africa
```

Or, if the environment already exists:

```bash
conda activate africa
```

Commands can also be run without activating the environment:

```bash
conda run -n africa python scripts/recompute_index_available_weights.py
```

## Reproducibility Workflow

Run commands from the repository root.

Recompute the final index and missing-data diagnostics:

```bash
python scripts/recompute_index_available_weights.py
python scripts/update_missing_data_tables.py
```

Generate robustness and result tables:

```bash
python scripts/export_chapter4_tables.py
python scripts/compare_sensitivity_weights.py
python scripts/update_sensitivity_equal_weight_table.py
python scripts/update_indicator_change_analysis.py
```

Generate figures:

```bash
python scripts/export_distribution_graphs.py
python scripts/export_geographical_graphs.py
```

Prepare manuscript tables:

```bash
python scripts/prepare_doc_update_tables.py
python scripts/update_measuring_sdi_docx.py
```

## Notes on Figures

`scripts/export_distribution_graphs.py` generates the kernel-density figure,
the subsystem mean-score figure, and the indicator-change heatmap.

`scripts/export_geographical_graphs.py` generates map figures and expects a
local world shapefile at:

```text
~/OneDrive/Rawdata/Geographic Information Data/World map/world_std.shp
```

The core index construction, weighting, robustness checks, and non-map figures
do not depend on this local shapefile.

## Software

The main analysis uses Python with pandas, NumPy, SciPy, scikit-learn,
statsmodels, matplotlib, seaborn, openpyxl, and geospatial packages listed in
`environment.yml`.
