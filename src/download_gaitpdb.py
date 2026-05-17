#!/usr/bin/env python3
"""Download and unpack the PhysioNet gaitpdb dataset."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path


DATA_URL = (
    "https://physionet.org/static/published-projects/gaitpdb/"
    "gait-in-parkinsons-disease-1.0.0.zip"
)
ZIP_NAME = "gait-in-parkinsons-disease-1.0.0.zip"


def run(args: list[str]) -> None:
    print("+ " + " ".join(args), flush=True)
    subprocess.run(args, check=True)


def download_with_python(url: str, output_path: Path) -> None:
    print(f"Downloading with Python stdlib: {url}", flush=True)
    with urllib.request.urlopen(url) as response, output_path.open("wb") as out:
        shutil.copyfileobj(response, out)


def download(url: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if shutil.which("aria2c"):
        run(
            [
                "aria2c",
                "--continue=true",
                "--max-tries=20",
                "--retry-wait=2",
                "--max-connection-per-server=8",
                "--split=8",
                "--min-split-size=1M",
                "--dir",
                str(output_path.parent),
                "--out",
                output_path.name,
                url,
            ]
        )
        return

    if shutil.which("curl"):
        run(
            [
                "curl",
                "-L",
                "--fail",
                "--show-error",
                "--continue-at",
                "-",
                "--output",
                str(output_path),
                url,
            ]
        )
        return

    download_with_python(url, output_path)


def extract(zip_path: Path, extract_dir: Path) -> None:
    extract_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as archive:
        archive.extractall(extract_dir)


def valid_zip(path: Path) -> bool:
    return path.exists() and zipfile.is_zipfile(path)


def count_gait_records(extract_dir: Path) -> int:
    return sum(
        1
        for path in extract_dir.rglob("*.txt")
        if path.name[:2] in {"Ga", "Ju", "Si"} and path.name[2:4] in {"Co", "Pt"}
    )


def write_dataset_note(data_root: Path, extract_dir: Path, record_count: int) -> None:
    note = data_root / "README.md"
    note.write_text(
        "\n".join(
            [
                "# PhysioNet gaitpdb local data",
                "",
                f"Source: {DATA_URL}",
                "Project page: https://physionet.org/content/gaitpdb/1.0.0/",
                "License: Open Data Commons Attribution License v1.0",
                "",
                f"Extracted directory: {extract_dir}",
                f"Detected gait record files: {record_count}",
                "",
                "Filename convention: Ga/Ju/Si = study, Co = control, Pt = PD patient.",
                "Each gait record has 19 whitespace-separated columns sampled at 100 Hz.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, default=Path("data/gaitpdb"))
    parser.add_argument("--url", default=DATA_URL)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    zip_path = args.data_root / ZIP_NAME
    extract_dir = args.data_root / "1.0.0"

    if args.force and zip_path.exists():
        zip_path.unlink()

    if not valid_zip(zip_path):
        if zip_path.exists():
            print(f"Found incomplete ZIP, resuming download: {zip_path}", flush=True)
        download(args.url, zip_path)
    else:
        print(f"Valid ZIP already exists: {zip_path}", flush=True)

    if not valid_zip(zip_path):
        raise RuntimeError(f"Downloaded file is still not a valid ZIP: {zip_path}")

    if args.force and extract_dir.exists():
        shutil.rmtree(extract_dir)

    if not count_gait_records(extract_dir):
        print(f"Extracting {zip_path} -> {extract_dir}", flush=True)
        extract(zip_path, extract_dir)
    else:
        print(f"Dataset already extracted: {extract_dir}", flush=True)

    record_count = count_gait_records(extract_dir)
    write_dataset_note(args.data_root, extract_dir, record_count)
    print(f"Done. Detected {record_count} gait record files.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
