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

如果 PhysioNet 下载慢，可以走本机 VPN 代理，例如 Clash/V2Ray 常见端口 `7890`：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\bootstrap_windows.ps1 -Proxy http://127.0.0.1:7890
```

也可以只下载/解压数据：

```powershell
.\.venv\Scripts\python.exe src\download_gaitpdb.py --proxy http://127.0.0.1:7890
```

## Model comparison

Windows 接手后新增了 subject-level repeated CV 模型对比脚本，默认复用已提交的小特征表：

```powershell
.\.venv\Scripts\python.exe src\run_model_comparison.py
```

默认实验协议：5 repeats x 5 folds，`StratifiedGroupKFold`，按 `subject_id` 分组，保证每个 fold 里同一受试者不会同时出现在 train/test。

当前结果（`results/model_comparison_summary.csv`）：

| model | accuracy | balanced accuracy | macro-F1 | ROC-AUC |
| --- | ---: | ---: | ---: | ---: |
| SVM-RBF | 0.778 +/- 0.074 | 0.773 +/- 0.071 | 0.754 +/- 0.076 | 0.859 +/- 0.066 |
| Extra Trees | 0.797 +/- 0.071 | 0.745 +/- 0.082 | 0.752 +/- 0.083 | 0.848 +/- 0.067 |
| Gradient Boosting | 0.774 +/- 0.072 | 0.735 +/- 0.079 | 0.733 +/- 0.082 | 0.809 +/- 0.076 |
| Random Forest | 0.798 +/- 0.060 | 0.734 +/- 0.075 | 0.745 +/- 0.075 | 0.855 +/- 0.064 |
| KNN-7 | 0.715 +/- 0.078 | 0.710 +/- 0.073 | 0.688 +/- 0.076 | 0.761 +/- 0.082 |
| Logistic Regression | 0.714 +/- 0.111 | 0.709 +/- 0.086 | 0.689 +/- 0.103 | 0.785 +/- 0.081 |
