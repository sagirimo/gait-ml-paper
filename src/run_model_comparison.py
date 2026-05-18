#!/usr/bin/env python3
"""Subject-level repeated cross-validation for gaitpdb feature baselines."""

from __future__ import annotations

import argparse
import json
import os
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
from sklearn.base import clone
from sklearn.ensemble import ExtraTreesClassifier, GradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score, roc_auc_score
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC


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


def build_models(random_state: int) -> dict[str, Pipeline]:
    models: dict[str, Pipeline] = {
        "logistic_regression": Pipeline(
            [
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
                (
                    "model",
                    LogisticRegression(
                        class_weight="balanced",
                        max_iter=5000,
                        random_state=random_state,
                    ),
                ),
            ]
        ),
        "svm_rbf": Pipeline(
            [
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
                (
                    "model",
                    SVC(
                        class_weight="balanced",
                        probability=True,
                        random_state=random_state,
                    ),
                ),
            ]
        ),
        "knn_7": Pipeline(
            [
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
                ("model", KNeighborsClassifier(n_neighbors=7)),
            ]
        ),
        "random_forest": Pipeline(
            [
                ("imputer", SimpleImputer(strategy="median")),
                (
                    "model",
                    RandomForestClassifier(
                        n_estimators=500,
                        class_weight="balanced",
                        n_jobs=-1,
                        random_state=random_state,
                    ),
                ),
            ]
        ),
        "extra_trees": Pipeline(
            [
                ("imputer", SimpleImputer(strategy="median")),
                (
                    "model",
                    ExtraTreesClassifier(
                        n_estimators=500,
                        class_weight="balanced",
                        n_jobs=-1,
                        random_state=random_state,
                    ),
                ),
            ]
        ),
        "gradient_boosting": Pipeline(
            [
                ("imputer", SimpleImputer(strategy="median")),
                ("model", GradientBoostingClassifier(random_state=random_state)),
            ]
        ),
    }

    try:
        from xgboost import XGBClassifier
    except ImportError:
        return models

    models["xgboost"] = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            (
                "model",
                XGBClassifier(
                    n_estimators=300,
                    max_depth=3,
                    learning_rate=0.05,
                    subsample=0.9,
                    colsample_bytree=0.9,
                    eval_metric="logloss",
                    random_state=random_state,
                ),
            ),
        ]
    )
    return models


def score_model(model: Pipeline, X_test: pd.DataFrame, y_test: pd.Series) -> dict[str, float]:
    y_pred = model.predict(X_test)
    if hasattr(model, "predict_proba"):
        y_score = model.predict_proba(X_test)[:, 1]
    else:
        y_score = model.decision_function(X_test)

    return {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_test, y_pred)),
        "macro_f1": float(f1_score(y_test, y_pred, average="macro")),
        "roc_auc": float(roc_auc_score(y_test, y_score)),
    }


def run_repeated_cv(
    features: pd.DataFrame,
    repeats: int,
    folds: int,
    random_state: int,
) -> pd.DataFrame:
    feature_cols = [column for column in features.columns if column not in META_COLUMNS]
    X = features[feature_cols].replace([np.inf, -np.inf], np.nan)
    y = features["label"].astype(int)
    groups = features["subject_id"]

    rows: list[dict[str, object]] = []
    for repeat in range(repeats):
        splitter = StratifiedGroupKFold(
            n_splits=folds,
            shuffle=True,
            random_state=random_state + repeat,
        )
        models = build_models(random_state + repeat)
        for fold, (train_idx, test_idx) in enumerate(splitter.split(X, y, groups), start=1):
            train_subjects = set(groups.iloc[train_idx])
            test_subjects = set(groups.iloc[test_idx])
            overlap = train_subjects.intersection(test_subjects)
            if overlap:
                raise RuntimeError(f"Subject leakage detected: {sorted(overlap)[:5]}")

            for model_name, estimator in models.items():
                print(f"repeat={repeat + 1}/{repeats} fold={fold}/{folds} model={model_name}", flush=True)
                model = clone(estimator)
                model.fit(X.iloc[train_idx], y.iloc[train_idx])
                metrics = score_model(model, X.iloc[test_idx], y.iloc[test_idx])
                rows.append(
                    {
                        "model": model_name,
                        "repeat": repeat + 1,
                        "fold": fold,
                        "n_train_records": int(len(train_idx)),
                        "n_test_records": int(len(test_idx)),
                        "n_train_subjects": int(len(train_subjects)),
                        "n_test_subjects": int(len(test_subjects)),
                        **metrics,
                    }
                )
    return pd.DataFrame(rows)


def summarize(cv_results: pd.DataFrame) -> pd.DataFrame:
    metric_cols = ["accuracy", "balanced_accuracy", "macro_f1", "roc_auc"]
    summary = cv_results.groupby("model")[metric_cols].agg(["mean", "std"]).reset_index()
    summary.columns = [
        "_".join(column).rstrip("_") if isinstance(column, tuple) else column
        for column in summary.columns
    ]
    return summary.sort_values("balanced_accuracy_mean", ascending=False)


def plot_summary(summary: pd.DataFrame, output_path: Path) -> None:
    plot_df = summary.sort_values("balanced_accuracy_mean")
    fig_height = max(4.0, 0.45 * len(plot_df))
    fig, ax = plt.subplots(figsize=(8.5, fig_height))
    ax.barh(
        plot_df["model"],
        plot_df["balanced_accuracy_mean"],
        xerr=plot_df["balanced_accuracy_std"],
        color="#386641",
        alpha=0.9,
    )
    ax.set_xlabel("Balanced accuracy, mean +/- SD")
    ax.set_ylabel("")
    ax.set_xlim(0.0, 1.0)
    ax.set_title("Subject-level repeated CV model comparison")
    fig.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--features-csv", type=Path, default=Path("data/processed/gaitpdb_features.csv"))
    parser.add_argument("--output-dir", type=Path, default=Path("results"))
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--random-state", type=int, default=42)
    args = parser.parse_args()

    features = pd.read_csv(args.features_csv)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    cv_results = run_repeated_cv(features, args.repeats, args.folds, args.random_state)
    summary = summarize(cv_results)

    cv_path = args.output_dir / "model_comparison_cv_results.csv"
    summary_path = args.output_dir / "model_comparison_summary.csv"
    plot_path = args.output_dir / "model_comparison_balanced_accuracy.png"
    json_path = args.output_dir / "model_comparison_summary.json"

    cv_results.to_csv(cv_path, index=False)
    summary.to_csv(summary_path, index=False)
    plot_summary(summary, plot_path)
    json_path.write_text(summary.to_json(orient="records", indent=2), encoding="utf-8")

    print(summary.to_string(index=False))
    print(json.dumps({"cv_results": str(cv_path), "summary": str(summary_path)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
