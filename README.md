# Sustainable Development Index for Sub-Saharan Africa

This repository contains the reproducible code and working data used for the
paper on measuring sustainable development in 45 Sub-Saharan African countries
from 2001 to 2021.

## Repository Layout

- `scripts/`: Python scripts for index reconstruction, robustness checks,
  tables, figures, and manuscript table updates.
- `notebooks/`: original exploratory and data-preparation notebooks.
- `figures/`: generated figures used in the manuscript.
- `output/indicator_change_analysis_2001_2021/`: generated indicator-change
  evidence tables and notes.
- `manuscript/`: manuscript drafts and the current Word document.
- Root-level `.csv` and `.xlsx` files: working inputs and generated tables kept
  with their original filenames so the scripts remain directly reproducible.

## Environment

The project uses the local conda environment named `africa`.

```bash
conda activate africa
```

Or run a command without activating the environment:

```bash
conda run -n africa python scripts/recompute_index_available_weights.py
```

For a fresh environment, `environment.yml` records the main packages used by the
scripts and notebooks.

## Main Workflow

Run scripts from the repository root:

```bash
python scripts/recompute_index_available_weights.py
python scripts/update_missing_data_tables.py
python scripts/export_chapter4_tables.py
python scripts/compare_sensitivity_weights.py
python scripts/update_sensitivity_equal_weight_table.py
python scripts/update_indicator_change_analysis.py
python scripts/export_distribution_graphs.py
python scripts/export_geographical_graphs.py
```

The manuscript update workflow uses temporary table files:

```bash
python scripts/prepare_doc_update_tables.py
python scripts/update_measuring_sdi_docx.py
```

`scripts/export_geographical_graphs.py` expects the local shapefile
`~/OneDrive/Rawdata/Geographic Information Data/World map/world_std.shp`.

## Notes

The scripts now locate the repository root from their own file path instead of
using a machine-specific absolute path.
