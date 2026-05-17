# Gait ML Paper — 项目初始化

**创建**: 2026-05-10
**目标**: 6 个月内出一篇 Sensors（MDPI）期刊论文
**方向**: 公开步态数据集 + ML 对比实验 + 实验室传感器验证

## 核心文件
- `马康_步态ML论文_执行手册.md` — 四阶段执行计划
- `步态ML_PubMed文献.ris` — 8 篇参考论文（导入 Zotero）

## 关键联系人
- **马康**（北理工）— 实验室设备 + 验证数据
- **OPEncode（本对话）** — 策略 + 申请

## 今天第一件事
打开 PhysioNet 下载公开步态数据集，跑一个 Random Forest Baseline。

## Phase 1 baseline

数据集：PhysioNet Gait in Parkinson's Disease v1.0.0  
任务：healthy control vs Parkinson's Disease patient

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --proxy '' -r requirements.txt -i https://pypi.org/simple
.venv/bin/python src/download_gaitpdb.py
.venv/bin/python src/run_rf_baseline.py
```

当前 baseline 使用 subject-level split，默认排除 `walk=10` dual-task 记录，避免同一受试者同时出现在训练集和测试集。

当前结果：
- accuracy: 0.800
- balanced accuracy: 0.758
- macro-F1: 0.769
- ROC-AUC: 0.872

结果文件在 `results/`，特征表在 `data/processed/gaitpdb_features.csv`。

## Windows handoff

Windows 高算力机器接手时先读：

- `docs/WINDOWS_CODEX_HANDOFF.md`
- `skills/gait-ml-paper/SKILL.md`

PowerShell 一键复现：

```powershell
.\scripts\bootstrap_windows.ps1
```
