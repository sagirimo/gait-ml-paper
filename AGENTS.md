# Gait ML Paper — Project AGENTS.md

## 项目目标
6 个月内发一篇 Sensors (MDPI, IF 3.4) 期刊论文，方向：公开步态数据集 + ML 对比实验 + 实验室传感器验证。

## 当前阶段：Phase 1 启动（5.10 — 5.17）
- [x] 下载 PhysioNet 公开步态数据集 (https://physionet.org/content/gaitpdb/1.0.0/)
- [x] 跑 Random Forest Baseline
- [ ] 跟马康确认实验室验证数据采集

## Phase 1 同步记录

### 2026-05-17 — Codex
- 数据集已下载并解压到 `data/gaitpdb/1.0.0/`，完整 ZIP 保存在 `data/gaitpdb/gait-in-parkinsons-disease-1.0.0.zip`。
- PhysioNet `gaitpdb` 实际是 Parkinson's Disease vs healthy controls 数据集，不包含中风；文件为 19 列 whitespace `.txt` time series，不是 CSV。
- 新增 `src/download_gaitpdb.py`：可复现下载、断点续传、解压、记录本地数据说明。
- 新增 `src/run_rf_baseline.py`：提取 trial-level force/symmetry/contact features，默认排除 `walk=10` dual-task 记录，按 subject 分组 train/test split，训练 Random Forest。
- 本地环境：已用 Homebrew 安装 `aria2`；项目内 `.venv` 已安装 `requirements.txt`。
- Baseline 输入：279 条 normal-walk trials，165 个 subjects；特征表 `data/processed/gaitpdb_features.csv`，shape = 279 x 266。
- Baseline 切分：train 123 subjects / 219 trials，test 42 subjects / 60 trials，避免同一 subject 同时出现在训练和测试。
- Random Forest 结果：accuracy 0.800，balanced accuracy 0.758，macro-F1 0.769，ROC-AUC 0.872；control F1 0.684，PD F1 0.854。
- 结果文件：`results/rf_baseline_metrics.csv`、`results/rf_baseline_classification_report.txt`、`results/rf_baseline_confusion_matrix.png`、`results/rf_baseline_feature_importance.csv`、`results/rf_baseline_feature_importance_top25.png`。
- Windows 交接：新增 `docs/WINDOWS_CODEX_HANDOFF.md`、`scripts/bootstrap_windows.ps1`、`skills/gait-ml-paper/SKILL.md`。Windows Codex 接手时先读这三个文件和 `README.md`。

## 文件结构
- `马康_步态ML论文_执行手册.md` — 四阶段完整计划 + 实验设计
- `马康_找方向指南_2026-05-10.md` — 选题背景 + 期刊选择
- `步态ML_PubMed文献.ris` — 参考文献（可导入 Zotero）
- `README.md` — 项目概要

## 关键人物
- **马康**（北理工）— 课题导师，提供实验室设备 + 验证数据

## 双端协作模式
- **Codex (GPT-5.x)** — 主力，承担核心代码 + 论文写作
- **OpenCode (DeepSeek V4)** — 辅助，接手 Codex 额度用完后的任务，负责文献检索 (Zotero MCP)、系统操作

## 可用技能/工具
- **Zotero MCP**: `zotero-mcp` 本地运行，端口 23119，可搜索、管理论文文献
- **SSH**: `ssh tokyo` 可连接东京云服务器
- **Python**: 主开发语言，环境在 MacBook 本地

## 开发环境
- macOS (MacBook)，Python 3，无特殊虚拟环境
- 数据目录建议：`./data/` 存放下载的数据集
- 代码目录建议：`./src/` 存放实验脚本

## 风格偏好
- 中文交流，技术术语保留英文
- 先做后说，不要过度解释
- 实验结果记入表格，图表用 matplotlib
