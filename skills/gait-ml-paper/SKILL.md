---
name: gait-ml-paper
description: Use for continuing the Gait ML Paper project: PhysioNet gaitpdb data download, feature extraction, Random Forest and model comparison baselines, Windows handoff, and Sensors manuscript experiments.
---

# Gait ML Paper Skill

## First Files To Read

1. `AGENTS.md` for the checklist, project stage, and collaboration state.
2. `README.md` for setup and reproduction commands.
3. `docs/WINDOWS_CODEX_HANDOFF.md` when working from the Windows high-compute machine.

## Data Policy

- Do not commit raw PhysioNet ZIP/extracted data or `.venv`.
- Reproduce data locally with `src/download_gaitpdb.py`.
- Source dataset: PhysioNet `gaitpdb` v1.0.0, Parkinson's Disease vs healthy controls.
- Data files are 19-column whitespace time series sampled at 100 Hz.

## Baseline Workflow

Create a virtual environment, install `requirements.txt`, download data, then run:

```bash
python src/run_rf_baseline.py
```

The current baseline:

- Extracts trial-level force/symmetry/contact features from VGRF time series.
- Excludes `walk=10` dual-task trials by default.
- Uses subject-level train/test split to avoid leakage.
- Saves metrics, classification report, confusion matrix, and feature importance in `results/`.

## Current Result To Preserve

- 279 normal-walk trials, 165 subjects.
- Random Forest accuracy 0.800, balanced accuracy 0.758, macro-F1 0.769, ROC-AUC 0.872.

## Next Good Tasks

- Add model comparison: XGBoost, SVM, KNN, Logistic Regression.
- Add repeated subject-level cross-validation.
- Add optional 1D-CNN/LSTM baseline for raw time series on the Windows/GPU machine.
- Draft Methods/Results tables from `results/`.
- Confirm lab validation data collection with Ma Kang.
