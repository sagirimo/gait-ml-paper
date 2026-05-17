# Windows Codex Handoff

## Mission

Continue the Gait ML Paper project on the high-compute Windows machine.

Paper direction: public gait sensor dataset + reproducible machine learning baselines + lab sensor validation for a Sensors-style applied ML paper.

## Current State

- Phase 1 dataset download: complete on Mac.
- Phase 1 Random Forest baseline: complete.
- Raw data is intentionally not committed to GitHub. Re-download it on Windows.
- Current dataset: PhysioNet `gaitpdb` v1.0.0, Parkinson's Disease vs healthy controls.
- Current baseline result: accuracy 0.800, balanced accuracy 0.758, macro-F1 0.769, ROC-AUC 0.872.

## Repository Layout

- `AGENTS.md`: project status, checklist, collaboration notes.
- `README.md`: reproducible setup and baseline commands.
- `src/download_gaitpdb.py`: downloads and extracts PhysioNet gaitpdb.
- `src/run_rf_baseline.py`: extracts features and runs Random Forest baseline.
- `requirements.txt`: Python dependencies.
- `results/`: small result artifacts from the first RF baseline.
- `skills/gait-ml-paper/SKILL.md`: project-specific Codex skill/instructions.

## Windows Setup

Use PowerShell from the repository root:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe src\download_gaitpdb.py
.\.venv\Scripts\python.exe src\run_rf_baseline.py
```

If downloads are slow, install `aria2` and rerun `src\download_gaitpdb.py`. The script automatically uses `aria2c` when available.

## Data Rules

Do not commit:

- `data/gaitpdb/*.zip`
- `data/gaitpdb/1.0.0/`
- `.venv/`
- large raw/intermediate files

It is acceptable to commit small reproducible artifacts such as:

- code
- README/docs
- small CSV result summaries
- figures in `results/`

## Next Tasks

1. Add model comparison experiments: SVM, KNN, Logistic Regression, XGBoost if available.
2. Add repeated subject-level cross-validation, not random row split.
3. Add a raw time-series baseline for the Windows high-compute machine, e.g. 1D-CNN or LSTM.
4. Generate a clean experiment table for the paper.
5. Ask Ma Kang about lab validation data collection and document protocol.

## Important Method Rule

Always split by subject, not by row/trial. If the same subject appears in both train and test, metrics are likely inflated by identity leakage.

## Codex Startup Prompt For Windows

Paste this to Windows Codex after cloning:

```text
Read AGENTS.md, README.md, docs/WINDOWS_CODEX_HANDOFF.md, and skills/gait-ml-paper/SKILL.md first.
Continue the Gait ML Paper project. Recreate the Python environment, download PhysioNet gaitpdb with src/download_gaitpdb.py, rerun src/run_rf_baseline.py, then add subject-level model comparison experiments. Keep raw data out of git. Update AGENTS.md after each completed task.
```
