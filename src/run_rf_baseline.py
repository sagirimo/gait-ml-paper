#!/usr/bin/env python3
"""Random Forest baseline for PhysioNet gaitpdb control vs PD classification."""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path

PLOT_CACHE_DIR = Path("results/.cache").resolve()
PLOT_CACHE_DIR.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("XDG_CACHE_HOME", str(PLOT_CACHE_DIR))
os.environ.setdefault("MPLCONFIGDIR", str(PLOT_CACHE_DIR / "matplotlib"))

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


FILE_RE = re.compile(
    r"^(?P<study>Ga|Ju|Si)(?P<group>Co|Pt)(?P<subject>\d+)_(?P<walk>\d+)\.txt$"
)
LEFT_SENSORS = [f"L{i}" for i in range(1, 9)]
RIGHT_SENSORS = [f"R{i}" for i in range(1, 9)]
COLUMNS = ["time", *LEFT_SENSORS, *RIGHT_SENSORS, "L_total", "R_total"]
META_COLUMNS = {
    "file",
    "file_name",
    "study",
    "group",
    "subject",
    "subject_id",
    "walk",
    "label",
    "label_name",
}


def parse_record_name(path: Path) -> dict[str, str] | None:
    match = FILE_RE.match(path.name)
    if not match:
        return None
    meta = match.groupdict()
    meta["subject_id"] = f"{meta['study']}{meta['group']}{meta['subject']}"
    meta["label"] = 0 if meta["group"] == "Co" else 1
    meta["label_name"] = "control" if meta["group"] == "Co" else "pd"
    return meta


def iter_record_paths(data_dir: Path, include_dual_task: bool) -> list[tuple[Path, dict]]:
    records: list[tuple[Path, dict]] = []
    for path in sorted(data_dir.rglob("*.txt")):
        meta = parse_record_name(path)
        if meta is None:
            continue
        if not include_dual_task and meta["walk"] == "10":
            continue
        records.append((path, meta))
    return records


def safe_cv(values: pd.Series) -> float:
    mean = float(values.mean())
    std = float(values.std(ddof=0))
    return std / (abs(mean) + 1e-9)


def rms(values: pd.Series) -> float:
    arr = values.to_numpy(dtype=float)
    return float(np.sqrt(np.nanmean(arr * arr)))


def add_stats(features: dict[str, float], values: pd.Series, prefix: str) -> None:
    features[f"{prefix}_mean"] = float(values.mean())
    features[f"{prefix}_std"] = float(values.std(ddof=0))
    features[f"{prefix}_min"] = float(values.min())
    features[f"{prefix}_max"] = float(values.max())
    features[f"{prefix}_median"] = float(values.median())
    features[f"{prefix}_q25"] = float(values.quantile(0.25))
    features[f"{prefix}_q75"] = float(values.quantile(0.75))
    features[f"{prefix}_iqr"] = features[f"{prefix}_q75"] - features[f"{prefix}_q25"]
    features[f"{prefix}_rms"] = rms(values)
    features[f"{prefix}_cv"] = safe_cv(values)


def segment_durations(mask: np.ndarray, dt: float, state: bool) -> list[float]:
    if mask.size == 0:
        return []
    durations: list[float] = []
    start = 0
    current = bool(mask[0])
    for idx in range(1, mask.size):
        value = bool(mask[idx])
        if value != current:
            if current == state:
                durations.append((idx - start) * dt)
            start = idx
            current = value
    if current == state:
        durations.append((mask.size - start) * dt)
    return durations


def add_contact_features(
    features: dict[str, float], time: pd.Series, force: pd.Series, prefix: str
) -> None:
    force_arr = force.to_numpy(dtype=float)
    time_arr = time.to_numpy(dtype=float)
    dt = float(np.nanmedian(np.diff(time_arr))) if len(time_arr) > 1 else 0.01
    threshold = max(20.0, 0.05 * float(np.nanmax(force_arr)))
    contact = force_arr > threshold

    stance = segment_durations(contact, dt, True)
    swing = segment_durations(contact, dt, False)
    duration = max(float(time_arr[-1] - time_arr[0]), dt)

    features[f"{prefix}_contact_threshold"] = threshold
    features[f"{prefix}_contact_fraction"] = float(np.nanmean(contact))
    features[f"{prefix}_stance_count"] = float(len(stance))
    features[f"{prefix}_stance_rate_hz"] = float(len(stance) / duration)

    for name, durations in [("stance", stance), ("swing", swing)]:
        arr = np.asarray(durations, dtype=float)
        if arr.size:
            features[f"{prefix}_{name}_duration_mean"] = float(np.mean(arr))
            features[f"{prefix}_{name}_duration_std"] = float(np.std(arr))
            features[f"{prefix}_{name}_duration_cv"] = float(
                np.std(arr) / (abs(np.mean(arr)) + 1e-9)
            )
        else:
            features[f"{prefix}_{name}_duration_mean"] = np.nan
            features[f"{prefix}_{name}_duration_std"] = np.nan
            features[f"{prefix}_{name}_duration_cv"] = np.nan


def extract_features(path: Path, meta: dict) -> dict[str, object]:
    df = pd.read_csv(path, sep=r"\s+", header=None, names=COLUMNS, engine="python")
    df = df.apply(pd.to_numeric, errors="coerce").dropna(how="any")

    features: dict[str, object] = {
        "file": str(path),
        "file_name": path.name,
        "study": meta["study"],
        "group": meta["group"],
        "subject": meta["subject"],
        "subject_id": meta["subject_id"],
        "walk": int(meta["walk"]),
        "label": int(meta["label"]),
        "label_name": meta["label_name"],
        "sample_count": int(len(df)),
    }

    if len(df) < 2:
        return features

    time = df["time"]
    dt = float(np.nanmedian(np.diff(time.to_numpy(dtype=float))))
    features["duration_s"] = float(time.iloc[-1] - time.iloc[0])
    features["sampling_hz_est"] = float(1.0 / dt) if dt > 0 else np.nan

    for column in [*LEFT_SENSORS, *RIGHT_SENSORS, "L_total", "R_total"]:
        add_stats(features, df[column], column)

    for column in ["L_total", "R_total"]:
        diff = pd.Series(np.diff(df[column].to_numpy(dtype=float)))
        add_stats(features, diff, f"{column}_delta")
        add_contact_features(features, time, df[column], column)

    left = df["L_total"]
    right = df["R_total"]
    total = left + right
    diff = left - right
    abs_diff = diff.abs()

    add_stats(features, total, "both_total")
    add_stats(features, diff, "left_right_diff")
    add_stats(features, abs_diff, "left_right_absdiff")

    left_mean = float(left.mean())
    right_mean = float(right.mean())
    features["left_right_mean_ratio"] = left_mean / (right_mean + 1e-9)
    features["left_right_asymmetry_index"] = (left_mean - right_mean) / (
        0.5 * (left_mean + right_mean) + 1e-9
    )
    features["left_right_total_corr"] = float(left.corr(right))
    features["total_zero_fraction"] = float(np.mean(total.to_numpy(dtype=float) <= 20.0))
    return features


def build_feature_table(data_dir: Path, include_dual_task: bool) -> pd.DataFrame:
    records = iter_record_paths(data_dir, include_dual_task)
    if not records:
        raise FileNotFoundError(f"No gait record .txt files found under {data_dir}")

    rows = []
    for idx, (path, meta) in enumerate(records, start=1):
        print(f"[{idx}/{len(records)}] extracting {path.name}", flush=True)
        rows.append(extract_features(path, meta))
    return pd.DataFrame(rows)


def split_by_subject(
    features: pd.DataFrame, test_size: float, random_state: int
) -> tuple[pd.Series, pd.Series]:
    subjects = features[["subject_id", "label"]].drop_duplicates()
    train_subjects, test_subjects = train_test_split(
        subjects["subject_id"],
        test_size=test_size,
        random_state=random_state,
        stratify=subjects["label"],
    )
    return train_subjects, test_subjects


def plot_feature_importance(importances: pd.DataFrame, output_path: Path, top_n: int) -> None:
    top = importances.head(top_n).iloc[::-1]
    fig_height = max(4.0, 0.28 * len(top))
    fig, ax = plt.subplots(figsize=(9, fig_height))
    ax.barh(top["feature"], top["importance"], color="#2f6f9f")
    ax.set_xlabel("Random Forest importance")
    ax.set_ylabel("")
    ax.set_title(f"Top {len(top)} gaitpdb RF features")
    fig.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)


def run_baseline(
    features: pd.DataFrame,
    output_dir: Path,
    test_size: float,
    random_state: int,
) -> dict[str, float]:
    output_dir.mkdir(parents=True, exist_ok=True)

    feature_cols = [c for c in features.columns if c not in META_COLUMNS]
    X = features[feature_cols].replace([np.inf, -np.inf], np.nan)
    y = features["label"].astype(int)

    train_subjects, test_subjects = split_by_subject(features, test_size, random_state)
    train_mask = features["subject_id"].isin(train_subjects)
    test_mask = features["subject_id"].isin(test_subjects)

    model = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            (
                "rf",
                RandomForestClassifier(
                    n_estimators=500,
                    random_state=random_state,
                    class_weight="balanced",
                    n_jobs=-1,
                ),
            ),
        ]
    )

    model.fit(X.loc[train_mask], y.loc[train_mask])
    y_pred = model.predict(X.loc[test_mask])
    y_score = model.predict_proba(X.loc[test_mask])[:, 1]
    y_test = y.loc[test_mask]

    labels = ["control", "pd"]
    report_text = classification_report(y_test, y_pred, target_names=labels)
    report_dict = classification_report(y_test, y_pred, target_names=labels, output_dict=True)
    cm = confusion_matrix(y_test, y_pred, labels=[0, 1])

    metrics = {
        "n_records": int(len(features)),
        "n_subjects": int(features["subject_id"].nunique()),
        "n_train_records": int(train_mask.sum()),
        "n_test_records": int(test_mask.sum()),
        "n_train_subjects": int(train_subjects.nunique()),
        "n_test_subjects": int(test_subjects.nunique()),
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_test, y_pred)),
        "macro_f1": float(f1_score(y_test, y_pred, average="macro")),
        "roc_auc": float(roc_auc_score(y_test, y_score)),
        "control_f1": float(report_dict["control"]["f1-score"]),
        "pd_f1": float(report_dict["pd"]["f1-score"]),
    }

    (output_dir / "rf_baseline_classification_report.txt").write_text(
        report_text, encoding="utf-8"
    )
    (output_dir / "rf_baseline_metrics.json").write_text(
        json.dumps(metrics, indent=2), encoding="utf-8"
    )
    pd.DataFrame([metrics]).to_csv(output_dir / "rf_baseline_metrics.csv", index=False)

    fig, ax = plt.subplots(figsize=(5, 4.5))
    ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=labels).plot(
        ax=ax, values_format="d", colorbar=False, cmap="Blues"
    )
    ax.set_title("Random Forest baseline")
    fig.tight_layout()
    fig.savefig(output_dir / "rf_baseline_confusion_matrix.png", dpi=180)
    plt.close(fig)

    rf = model.named_steps["rf"]
    importances = (
        pd.DataFrame({"feature": feature_cols, "importance": rf.feature_importances_})
        .sort_values("importance", ascending=False)
        .reset_index(drop=True)
    )
    importances.to_csv(output_dir / "rf_baseline_feature_importance.csv", index=False)
    plot_feature_importance(
        importances, output_dir / "rf_baseline_feature_importance_top25.png", top_n=25
    )

    print(report_text)
    print(json.dumps(metrics, indent=2))
    return metrics


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path("data/gaitpdb/1.0.0"))
    parser.add_argument(
        "--features-csv", type=Path, default=Path("data/processed/gaitpdb_features.csv")
    )
    parser.add_argument("--output-dir", type=Path, default=Path("results"))
    parser.add_argument("--include-dual-task", action="store_true")
    parser.add_argument("--reuse-features", action="store_true")
    parser.add_argument("--test-size", type=float, default=0.25)
    parser.add_argument("--random-state", type=int, default=42)
    args = parser.parse_args()

    if args.reuse_features and args.features_csv.exists():
        features = pd.read_csv(args.features_csv)
    else:
        features = build_feature_table(args.data_dir, args.include_dual_task)
        args.features_csv.parent.mkdir(parents=True, exist_ok=True)
        features.to_csv(args.features_csv, index=False)

    run_baseline(features, args.output_dir, args.test_size, args.random_state)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
