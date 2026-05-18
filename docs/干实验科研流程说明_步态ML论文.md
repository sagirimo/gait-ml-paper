# 干实验科研流程说明：步态 ML 论文从 0 到投稿

创建日期：2026-05-17  
项目目录：`C:\Users\MOLIEX-DESKTOP\Documents\Project\gait-ml-paper`  
写给：有 wet 实验经历、医学背景较强、正在进入 dry lab / computational research 路线的你

## 0. 先说实话

你现在不是“不会计算机所以做不了”，而是处在一个很常见、也很有优势的位置：

- 你有医学和实验意识，知道一个研究最终要回答临床问题，而不是只追求模型分数。
- 你暂时不熟悉 Python、机器学习、数据泄漏、交叉验证这些 dry lab 语言。
- 这个项目适合作为入门：数据量不算巨大，任务明确，结果能复现，论文目标也不是顶级算法创新，而是“传感器数据 + 可复现实验 + 合理验证”。

最重要的一点：这篇论文不是要把你训练成计算机科班学生，而是要把你训练成一个能和工程工具合作、能判断实验设计是否靠谱、能把结果写成医学/传感器论文的人。

这份文档会回答五个问题：

1. 我们到底要做什么？
2. 现在已经完成了什么，还有什么 TODO？
3. 一个 dry lab 医学科研项目从想法到投稿，完整流程是什么？
4. 你需要学数学、Python、ML 到什么程度？
5. 学到什么程度就应该尽快给马康老师汇报？

## 1. 项目一句话版本

目标：在 6 个月内完成一篇面向 Sensors 的应用型机器学习论文。

论文方向：

> 使用公开步态传感器数据集建立 Parkinson's Disease 与 healthy control 的机器学习分类模型，并结合实验室采集的传感器数据做外部验证或可行性验证。

项目关键词：

- Gait analysis
- Wearable sensors / force sensors / plantar pressure
- Parkinson's Disease
- Machine learning
- Subject-level validation
- Lab sensor validation
- Sensors-style applied ML paper

## 2. 当前项目状态

### 2.1 已经完成

当前仓库已经完成了 Phase 1 的大部分工作：

- 已下载 PhysioNet `gaitpdb` v1.0.0 数据集。
- 已确认实际任务是 Parkinson's Disease vs healthy controls，不是中风。
- 已确认原始文件是 whitespace-separated `.txt` time series，不是 CSV。
- 已写好数据下载脚本：`src/download_gaitpdb.py`。
- 已写好 Random Forest baseline：`src/run_rf_baseline.py`。
- 已写好模型对比脚本：`src/run_model_comparison.py`。
- 已完成 Windows 环境复现。
- 已复现 RF baseline。
- 已完成 5 repeats x 5 folds subject-level cross-validation 的 classical ML 模型对比。
- 已连接 Zotero，并确认 collection `步态ML_PubMed文献` 存在。

### 2.2 当前数据

数据集：PhysioNet `gaitpdb` v1.0.0  
数据类型：vertical ground reaction force / foot sensor time series  
采样率：100 Hz  
任务：control vs Parkinson's Disease patient  
文件数量：306 个 gait record files  
当前 baseline 默认排除 dual-task walk 10 后：

- 279 条 normal-walk trials
- 165 个 subjects
- 特征表：`data/processed/gaitpdb_features.csv`
- 特征表 shape：279 x 266

### 2.3 当前 RF baseline 结果

Random Forest 使用 subject-level train/test split，避免同一个 subject 同时出现在 train/test：

| 指标 | 数值 |
|---|---:|
| accuracy | 0.800 |
| balanced accuracy | 0.758 |
| macro-F1 | 0.769 |
| ROC-AUC | 0.872 |
| control F1 | 0.684 |
| PD F1 | 0.854 |

一句话解读：

> 模型能比较稳定地区分 PD 与健康对照，PD 识别较好，但 control 类别略弱。结果有论文雏形，但还不能直接投稿，因为还缺少更系统的实验、解释和实验室验证。

### 2.4 当前模型对比结果

5x5 `StratifiedGroupKFold`，按 `subject_id` 分组：

| model | accuracy | balanced accuracy | macro-F1 | ROC-AUC |
|---|---:|---:|---:|---:|
| SVM-RBF | 0.778 +/- 0.074 | 0.773 +/- 0.071 | 0.754 +/- 0.076 | 0.859 +/- 0.066 |
| Extra Trees | 0.797 +/- 0.071 | 0.745 +/- 0.082 | 0.752 +/- 0.083 | 0.848 +/- 0.067 |
| Gradient Boosting | 0.774 +/- 0.072 | 0.735 +/- 0.079 | 0.733 +/- 0.082 | 0.809 +/- 0.076 |
| Random Forest | 0.798 +/- 0.060 | 0.734 +/- 0.075 | 0.745 +/- 0.075 | 0.855 +/- 0.064 |
| KNN-7 | 0.715 +/- 0.078 | 0.710 +/- 0.073 | 0.688 +/- 0.076 | 0.761 +/- 0.082 |
| Logistic Regression | 0.714 +/- 0.111 | 0.709 +/- 0.086 | 0.689 +/- 0.103 | 0.785 +/- 0.081 |

当前最佳：SVM-RBF，balanced accuracy `0.773 +/- 0.071`。

## 3. 现在有没有 TODO？

有，而且非常明确。按紧急程度排序：

### 3.1 今天/明天必须做

- [ ] 跟马康老师确认实验室验证数据能不能采。
- [ ] 确认实验室设备类型：压力地板、跑步机、足底压力鞋垫、IMU、运动捕捉，还是其他。
- [ ] 确认设备导出的原始数据格式：CSV、TXT、Excel、厂家软件格式。
- [ ] 确认采样率、传感器通道数、左右脚是否分开、有没有总压力或 GRF。
- [ ] 确认能否采健康人，能否采 PD/神经系统疾病/膝骨关节炎/康复患者。
- [ ] 确认是否需要伦理审批、知情同意、去标识化流程。

### 3.2 本周内要做

- [ ] 把现有模型对比结果整理成论文级表格。
- [ ] 生成一张更适合论文的 model comparison figure。
- [ ] 给每篇 Zotero 文献做 3-5 句精读摘要。
- [ ] 写 Methods 初稿骨架：dataset、feature extraction、models、validation protocol、metrics。
- [ ] 添加 feature selection 实验。
- [ ] 添加 feature ablation 实验。
- [ ] 设计 lab validation protocol 文档，拿给马老师确认。

### 3.3 之后 2-4 周要做

- [ ] 增加 raw time-series baseline，例如 1D-CNN 或 LSTM。
- [ ] 检查 dual-task walk 10 是否可以作为补充分析。
- [ ] 做模型校准或 threshold analysis。
- [ ] 做 feature importance / SHAP 解释。
- [ ] 如果能拿到实验室数据，写数据转换脚本。
- [ ] 如果实验室只采健康人，做 false-positive / domain-shift sanity check。
- [ ] 如果能采病人，做真正 external validation。

### 3.4 投稿前必须完成

- [ ] 所有实验结果表格固定下来。
- [ ] 所有图输出为论文分辨率。
- [ ] 写完 Introduction、Methods、Results、Discussion。
- [ ] 明确贡献点，避免过度声称临床诊断价值。
- [ ] 检查 Sensors 格式、参考文献、伦理声明、数据可用性声明。
- [ ] 和马老师确认作者顺序、经费、版面费、投稿期刊。

## 4. 论文的科学问题应该怎么讲

不要把论文讲成“我跑了几个模型，哪个准确率高”。这会显得很弱。

更好的讲法是：

> 步态异常是 Parkinson's Disease 等神经运动障碍的重要表现。公开步态传感器数据提供了可复现的模型开发基础，但机器学习研究容易出现 subject leakage、验证不足和外部传感器适配不足。本研究基于 PhysioNet gaitpdb 数据集，构建可复现的 subject-level ML pipeline，比较多种 classical ML 和 raw time-series 模型，并结合实验室传感器数据评估模型在真实采集环境中的可迁移性。

拆成三个层次：

1. 临床问题：步态是否能反映神经运动障碍？
2. 工程问题：传感器信号能否稳定提取可用特征？
3. 方法学问题：模型评估是否避免泄漏，是否能跨数据来源验证？

## 5. 你作为医学生，真正需要负责什么

你不需要一开始就能手写所有代码。你需要逐步能判断这些东西：

### 5.1 临床和实验设计判断

你要能回答：

- 这个任务的疾病标签是什么？
- control 和 patient 的定义是什么？
- 纳入排除标准是什么？
- 实验室采集的人群和公开数据集的人群是否可比？
- 采集方案会不会引入偏差？
- 模型结果能不能被临床解释？
- 论文结论有没有过度推断？

### 5.2 数据判断

你要能回答：

- 一行数据代表一个时间点，还是一个 trial？
- 一个 subject 有几个 trials？
- label 是 subject-level 还是 trial-level？
- train/test split 是按 subject 分，还是按 trial 随机分？
- 有没有同一个人同时进入训练集和测试集？
- 缺失值怎么处理？
- 不同设备数据单位是否一致？

### 5.3 结果判断

你要能回答：

- accuracy 为什么不够？
- balanced accuracy 为什么重要？
- macro-F1 代表什么？
- ROC-AUC 代表什么？
- confusion matrix 哪一类错得多？
- 模型高分是不是可能因为 data leakage？
- 实验室验证数据能支持多强的结论？

这些判断比“会不会写复杂神经网络”更重要。

## 6. 机器学习基本概念，用医学语言解释

### 6.1 Dataset

Dataset 就是你的实验材料。

wet lab 里你有样本、组织、细胞、动物；dry lab 里你有数据表、时间序列、图像、测序矩阵。

本项目里 dataset 是：

- 多个受试者的步态传感器时间序列。
- 每个文件是一次 walking trial。
- 每个 subject 属于 control 或 PD。

### 6.2 Feature

Feature 是模型看的变量。

医学里类似：

- 年龄
- 性别
- 血压
- CRP
- 肿瘤大小
- 基因表达量

本项目里的 feature 例如：

- 左脚总压力均值
- 右脚总压力变异系数
- 左右脚压力差
- stance duration
- swing duration
- contact fraction
- 左右脚相关性

### 6.3 Label

Label 是模型要预测的答案。

本项目：

- `0` = healthy control
- `1` = Parkinson's Disease patient

### 6.4 X 和 y

机器学习里经常写：

- `X` = features，也就是输入变量
- `y` = labels，也就是答案

你可以理解成：

```text
X = 患者的检查指标
y = 患者真实诊断
```

模型训练就是让机器学习 `X -> y` 的映射关系。

### 6.5 Train/Test Split

训练集和测试集相当于：

- train：拿来学习规律的样本
- test：完全没见过，用来考试的样本

关键：同一个 subject 不能同时出现在 train 和 test。

如果同一个人出现在两边，模型可能不是学到了 PD 步态，而是记住了这个人的个体特征。这叫 data leakage。

### 6.6 Cross-validation

Cross-validation 是重复分训练集/测试集，避免某一次随机切分刚好幸运或倒霉。

我们现在用的是：

- 5 folds
- 5 repeats
- subject-level grouping

意思是：

> 重复 5 次，每次把 subject 分成 5 份，轮流用其中 1 份测试、4 份训练。

### 6.7 Model

Model 是从 feature 到 label 的规则。

本项目现在有：

- Logistic Regression：线性、可解释、基础模型。
- SVM-RBF：适合非线性边界，目前表现最好。
- KNN：看最近邻样本投票。
- Random Forest：很多 decision trees 投票。
- Extra Trees：更随机的 tree ensemble。
- Gradient Boosting：一棵树接一棵树纠错。

后续可能加：

- XGBoost：常用强 baseline。
- 1D-CNN：直接看时间序列局部模式。
- LSTM/GRU：直接看时间序列动态变化。

### 6.8 Metrics

不同指标回答不同问题。

accuracy：

> 总共猜对多少。

问题：如果 PD 比 control 多，模型全猜 PD 也可能 accuracy 看起来不低。

balanced accuracy：

> 分别看 control 和 PD 的识别能力，再取平均。

本项目建议把 balanced accuracy 当作主指标之一。

macro-F1：

> 每一类的 precision 和 recall 综合后，再平均。

适合类别不平衡时使用。

ROC-AUC：

> 模型把 PD 排在 control 前面的能力。

它不依赖某一个固定 threshold，适合评价模型区分能力。

confusion matrix：

> 哪一类被错分成哪一类。

医学上最容易解释，因为你能看到 false positive 和 false negative。

## 7. 当前代码在做什么

### 7.1 `src/download_gaitpdb.py`

作用：

- 下载 PhysioNet gaitpdb zip。
- 支持断点续传。
- 支持代理。
- 解压到 `data/gaitpdb/1.0.0/`。
- 写入本地数据说明 `data/gaitpdb/README.md`。

你需要知道：

- 原始数据不进 git。
- 如果换电脑，用这个脚本重新下载。
- Windows 上如果直连失败，可以用代理 `http://127.0.0.1:7890`。

### 7.2 `src/run_rf_baseline.py`

作用：

- 读取 `.txt` time series。
- 从文件名解析 study、group、subject、walk。
- 默认排除 `walk=10` dual-task。
- 提取 trial-level features。
- 保存 `data/processed/gaitpdb_features.csv`。
- 按 subject 分 train/test。
- 训练 Random Forest。
- 输出 metrics、classification report、confusion matrix、feature importance。

你需要知道：

- 这个脚本是“第一个能跑通的主实验”。
- 它已经避免 subject leakage。
- 它是论文 Methods 里 feature extraction 和 baseline 的基础。

### 7.3 `src/run_model_comparison.py`

作用：

- 读取已提取好的特征表。
- 使用 5x5 subject-level repeated cross-validation。
- 比较多种模型。
- 输出完整 fold-level 结果和 summary。
- 画 balanced accuracy 对比图。

你需要知道：

- 这是论文 Exp 1 的基础。
- 当前 SVM-RBF 最好。
- 后面可以加入 XGBoost、1D-CNN/LSTM、feature selection、ablation。

## 8. Zotero 文献库怎么用

本次已连接 Zotero Desktop local API：

- Zotero version：9.0.3
- local API：已开启
- collection：`步态ML_PubMed文献`
- collection key：`K87R5HZW`

collection 里当前 8 篇文献：

| Zotero key | 年份 | 题目 | 期刊 | DOI |
|---|---:|---|---|---|
| YXRMVUPX | 2024 | Predicting the healing of lower extremity fractures using wearable ground reaction force sensors and machine learning | Sensors | 10.3390/s24165321 |
| MWCL75HW | 2024 | Gait alterations and association with worsening knee pain and physical function: a machine learning approach with wearable sensors in the multicenter osteoarthritis study | Arthritis Care & Research | 10.1002/acr.25327 |
| FQY66H53 | 2024 | Identifying changes in dynamic plantar pressure associated with radiological knee osteoarthritis based on machine learning and wearable devices | Journal of NeuroEngineering and Rehabilitation | 10.1186/s12984-024-01337-6 |
| WAZMUEU9 | 2024 | Motor assessment of X-linked dystonia parkinsonism via machine-learning-based analysis of wearable sensor data | Scientific Reports | 10.1038/s41598-024-63946-4 |
| KI53PAVP | 2024 | Machine learning model identifies patient gait speed throughout the episode of care, generating notifications for clinician evaluation | Gait & Posture | 10.1016/j.gaitpost.2024.09.001 |
| JPNQEWQG | 2024 | A machine learning contest enhances automated freezing of gait detection and reveals time-of-day effects | Nature Communications | 10.1038/s41467-024-49027-0 |
| NE52738X | 2024 | Leather-based shoe soles for real-time gait recognition and automatic remote assistance using machine learning | ACS Applied Materials & Interfaces | 10.1021/acsami.4c16505 |
| S6QZT38T | 2024 | Wearable online freezing of gait detection and cueing system | Bioengineering | 10.3390/bioengineering11101048 |

### 8.1 这些文献对我们有什么用

North et al. 2024：

- 说明 wearable ground reaction force sensors + ML 可以发表在 Sensors。
- 对我们目标期刊最直接有参考价值。

Bacon et al. 2024：

- 说明 wearable gait sensor features 可以和临床疼痛、功能恶化相关。
- 有助于 Introduction 里讲步态参数的临床意义。

Li et al. 2024：

- 说明 plantar pressure + ML 可以用于骨关节炎相关变化识别。
- 对实验室如果使用足底压力设备很有参考价值。

Parisi et al. 2024：

- 说明 wearable sensor data 可以用于运动障碍评估。
- 对我们做 PD/神经运动障碍方向有支撑。

Surmacz et al. 2024：

- 强调 gait speed / gait monitoring 可以嵌入 episode of care。
- 对 Discussion 里讲临床工作流价值有帮助。

Salomon et al. 2024：

- freezing of gait ML contest，说明 gait ML 领域重视 benchmark、挑战赛、时间因素。
- 对我们强调可复现和严谨验证有帮助。

Zhang et al. 2024：

- 说明鞋底传感器、远程辅助、实时识别是一个活跃方向。
- 对未来拓展 wearable device 有帮助。

Slemenšek et al. 2024：

- 在线 freezing of gait detection and cueing system。
- 对 real-time system 和临床辅助价值有帮助。

### 8.2 后续文献精读模板

每篇文献最好整理成下面格式：

```markdown
## 文献标题

- 研究问题：
- 数据来源：
- 传感器类型：
- 样本量：
- 标签/结局：
- ML 模型：
- 验证方式：
- 主要指标：
- 主要结果：
- 局限性：
- 对我们论文的启发：
```

精读的目标不是背论文，而是为 Introduction、Methods、Discussion 找材料。

## 9. 这类 dry lab 研究的完整流程

### 9.1 Step 1：确定临床问题

先问：

- 我们研究的疾病或状态是什么？
- 为什么步态能反映这个疾病？
- 这个问题有临床意义吗？
- 传感器方法比传统评估有什么优势？

本项目目前问题：

> 能否用步态传感器信号和机器学习区分 Parkinson's Disease 与健康对照？

进一步包装：

> 可复现的 subject-level ML pipeline 能否为步态异常筛查和实验室传感器验证提供基础？

### 9.2 Step 2：确定数据来源

数据可以来自：

- 公开数据库。
- 医院回顾性数据。
- 实验室前瞻采集。
- 多中心合作数据。

本项目：

- 公开数据：PhysioNet gaitpdb。
- 实验室数据：待马康老师确认。

注意：

- 公开数据用于开发和内部验证。
- 实验室数据用于外部验证或可行性验证。
- 如果实验室数据和公开数据设备差别很大，就会出现 domain shift。

### 9.3 Step 3：理解数据结构

这一步很关键，医学背景的人最容易跳过，但它决定后面会不会错。

你要弄清楚：

- 一个文件代表什么？
- 一行代表什么？
- 一列代表什么？
- label 在哪里？
- subject id 在哪里？
- 是否有重复测量？
- 是否有不同实验条件？

本项目：

- 一个 `.txt` 文件 = 一次 walking trial。
- 一行 = 一个时间点。
- 19 列 = time + 左脚 8 个 sensors + 右脚 8 个 sensors + 左脚总力 + 右脚总力。
- 文件名包含 group 和 subject。
- `Co` = control。
- `Pt` = PD patient。
- `walk=10` 是 dual-task，当前默认排除。

### 9.4 Step 4：数据清洗

清洗不是“让数据变漂亮”，而是让它能被公平分析。

本项目清洗包括：

- 读取 whitespace `.txt`。
- 强制转换为数字。
- 删除全空/异常行。
- 检查采样率估计。
- 提取 subject_id。
- 排除 dual-task walk 10。
- 把 inf 替换为 nan。
- 用 median imputer 填补缺失特征。

### 9.5 Step 5：特征工程

传统 ML 通常不直接吃原始时间序列，而是先提取 feature。

本项目提取：

- 每个传感器的 mean、std、min、max、median、IQR、RMS、CV。
- 左右脚总压力变化。
- contact fraction。
- stance duration。
- swing duration。
- 左右脚压力差。
- 左右脚不对称指数。
- 左右脚相关性。

医学解释：

- PD 可能影响步态节律、对称性、接触时间、压力分布。
- 这些特征是把原始力信号转换成可解释指标。

### 9.6 Step 6：先跑 baseline

baseline 是最低限度可工作的模型。

它的作用不是炫技，而是确认：

- 数据能读。
- 标签能解析。
- 特征有信息量。
- train/test 没有明显错误。
- 结果比随机猜测好。

本项目 baseline：

- Random Forest。
- subject-level split。
- balanced class weight。
- 输出 metrics 和图。

### 9.7 Step 7：避免 data leakage

这是这篇论文最需要守住的底线。

错误做法：

> 把 279 条 trials 随机分 train/test。

为什么错：

- 同一个 subject 可能有多次 trials。
- 如果同一个 subject 出现在 train 和 test，模型可能记住个体特征。
- 分数会虚高。

正确做法：

> 按 subject_id 分组，保证同一个 subject 只在 train 或 test 一边。

我们现在已经这样做了。

### 9.8 Step 8：模型对比

一篇应用型 ML 论文通常不能只给一个模型。

需要比较：

- 简单线性模型。
- 非线性模型。
- tree-based ensemble。
- 距离模型。
- 可能再加深度学习模型。

本项目已经比较：

- Logistic Regression
- SVM-RBF
- KNN-7
- Random Forest
- Extra Trees
- Gradient Boosting

后续建议加：

- XGBoost
- 1D-CNN
- LSTM/GRU

### 9.9 Step 9：特征筛选和消融

审稿人会问：

> 模型到底靠什么判断？是不是所有特征都需要？

所以要做：

feature selection：

- Filter：按统计相关性或 mutual information 选。
- Wrapper：递归特征消除，例如 RFE。
- Embedded：用 Random Forest / L1 Logistic 等自带重要性。

ablation：

- 去掉单传感器统计特征。
- 去掉左右脚对称性特征。
- 去掉 contact/stance/swing 特征。
- 看性能下降多少。

这样 Discussion 才能讲：

> 哪些类型的 gait features 对 PD classification 更重要。

### 9.10 Step 10：解释模型

医学论文不能只说模型准，还要说为什么。

可用解释：

- Random Forest feature importance。
- Permutation importance。
- SHAP。
- 组级 feature importance。
- 结合 clinical gait knowledge 解释。

当前 top RF features 包括：

- `L7_cv`
- `L5_cv`
- `R6_cv`
- `R_total_swing_duration_mean`
- `left_right_absdiff_cv`
- `R_total_contact_fraction`
- `L_total_contact_fraction`

初步解释方向：

> 压力信号变异性、左右不对称、足部接触/摆动时间可能与 PD 步态异常相关。

这只是初步解释，不能过度说成机制证明。

### 9.11 Step 11：实验室验证

这是本项目的关键卖点，也是最大不确定性。

最强版本：

- 实验室采健康人和 PD/神经运动障碍患者。
- 使用相近传感器。
- 公开数据训练模型。
- 实验室数据作为 external validation。

中等版本：

- 实验室采健康人和某类步态异常患者，例如膝关节、康复、神经病变。
- 任务可能改成 healthy vs abnormal gait。
- 需要谨慎说明疾病标签不同。

最低可行版本：

- 只采 5-10 个健康人。
- 不能证明 PD classifier 的 clinical generalization。
- 只能做：
  - 数据采集流程验证。
  - 特征提取兼容性验证。
  - healthy external sanity check。
  - false positive rate 检查。
  - feature distribution comparison。

必须说实话：

> 如果实验室只采健康人，这不是完整 external validation，只能称为 feasibility validation 或 lab sensor sanity validation。论文可以写，但结论要收敛。

### 9.12 Step 12：论文写作

论文不是最后才写。Methods 可以从现在开始写。

建议顺序：

1. Methods：最容易，因为按代码写。
2. Results：按表格和图写。
3. Introduction：等文献精读后写。
4. Discussion：等结果稳定后写。
5. Abstract：最后写。

## 10. 你需要学到什么程度

### 10.1 Python

最低可汇报水平：

- 能打开项目目录。
- 能知道 `.py` 是脚本。
- 能运行：

```powershell
.\.venv\Scripts\python.exe src\run_rf_baseline.py --reuse-features
.\.venv\Scripts\python.exe src\run_model_comparison.py
```

- 能知道 `pandas` 读表，`sklearn` 跑模型，`matplotlib` 画图。
- 能看懂 CSV 表头和结果文件。

不要求：

- 现在就能独立写完整 pipeline。
- 现在就能 debug 所有 Python 错误。
- 现在就能写深度学习框架。

1 个月目标：

- 能读懂脚本大结构。
- 能修改简单参数，例如 random_state、folds、output path。
- 能用 pandas 看数据维度、列名、缺失值。

3 个月目标：

- 能独立写一个小的 sklearn baseline。
- 能把实验结果整理成表格。
- 能根据审稿意见改分析。

### 10.2 数学

你不需要先把高数、线代、概率全学完再做项目。项目推进和数学学习可以并行。

最低可汇报水平：

- 均值 mean：平均水平。
- 标准差 std：波动程度。
- 变异系数 CV：标准差 / 均值，表示相对波动。
- 四分位数和 IQR：分布范围。
- 相关系数 correlation：两个信号同步变化程度。
- sensitivity/recall：病人里识别出多少。
- specificity：健康人里识别对多少。
- precision：模型说是病人时，有多少真是病人。
- F1：precision 和 recall 的折中。
- AUC：整体区分能力。

1 个月目标：

- 理解 train/test、cross-validation、overfitting。
- 理解为什么类别不平衡时 balanced accuracy 重要。
- 理解为什么 subject-level split 是医学重复测量数据的底线。

3 个月目标：

- 理解 logistic regression、SVM、Random Forest 的基本思想。
- 理解 feature selection 和 SHAP 的用途。
- 理解 confidence interval / standard deviation 在报告结果中的作用。

可以暂时不深究：

- SVM kernel 的完整数学推导。
- 神经网络反向传播公式。
- 随机森林泛化误差证明。

你需要先达到“能判断实验设计是否正确，能解释结果是否可信”，不是“能从公式推导模型”。

### 10.3 机器学习

最低可汇报水平：

- 知道这是 supervised classification。
- 知道 label 是 PD/control。
- 知道 features 来自 gait sensor。
- 知道模型训练后要在没见过的 subject 上测试。
- 知道当前 SVM-RBF 在 repeated CV 中最好。
- 知道 Random Forest baseline 已经复现。

1 个月目标：

- 能解释 5-6 个常用模型的区别。
- 能说明为什么要比较多个模型。
- 能读懂 confusion matrix。
- 能知道哪些结果适合写进论文。

3 个月目标：

- 能设计 ablation study。
- 能解释 feature importance。
- 能根据临床意义讨论模型发现。
- 能对审稿人质疑 data leakage、sample size、generalization 做回应。

## 11. 什么时候应该尽快给马康老师汇报

结论：现在就已经到第一次汇报门槛了。

不需要等你学完数学，也不需要等深度学习跑完。

### 11.1 第一次汇报门槛

只要你能讲清下面 8 点，就应该汇报：

1. 我们已经找到公开数据集：PhysioNet gaitpdb。
2. 数据集实际任务是 PD vs healthy control，不是中风。
3. 数据是足底/地面反作用力相关 time series，采样率 100 Hz。
4. 已经完成可复现 baseline。
5. Random Forest baseline accuracy 0.800，balanced accuracy 0.758，ROC-AUC 0.872。
6. 已经做了 subject-level model comparison，当前 SVM-RBF balanced accuracy 约 0.773。
7. 我们知道必须按 subject 分组，避免同一人进 train/test 造成泄漏。
8. 现在最需要马老师确认实验室传感器数据能不能采，以及能采什么人群。

你现在已经满足这些条件。

### 11.2 给马老师汇报的核心目的

第一次汇报不是展示你多懂计算机，而是拿到项目能不能落地的关键信息：

- 实验室有什么设备？
- 能不能导出原始数据？
- 能不能采 5-10 个健康人？
- 有没有可能采少量 PD/步态异常患者？
- 伦理和知情同意怎么走？
- 马老师是否认可 Sensors 方向？
- 版面费是否能走课题经费？

### 11.3 建议发给马老师的消息

可以直接发：

```text
马老师，我这两天把步态 ML 方向先跑通了一个公开数据 baseline。

目前用的是 PhysioNet gaitpdb 数据集，实际任务是 Parkinson's Disease vs healthy controls，数据是足底/地面反作用力相关的 100 Hz time-series。我已经做了可复现的数据下载、特征提取和 subject-level 机器学习验证，避免同一个受试者同时出现在训练集和测试集。

目前 Random Forest baseline 的 accuracy 是 0.800，balanced accuracy 是 0.758，ROC-AUC 是 0.872。进一步做了 5x5 subject-level cross-validation 的模型对比，目前 SVM-RBF 的 balanced accuracy 最好，大约 0.773 +/- 0.071。

下一步我想把公开数据训练和实验室传感器验证结合起来，形成一篇 Sensors 风格的应用型 ML 论文。想跟您确认一下实验室能不能采一小批步态传感器数据：比如 5-10 个健康人，每人正常步行 3 次，每次 30 秒；如果有机会采到 PD、膝关节或其他步态异常人群会更好。

我主要想确认：
1. 实验室目前可用的是压力地板、足底压力鞋垫、跑步机、IMU 还是运动捕捉？
2. 设备能不能导出原始 CSV/TXT 数据？
3. 采样率、左右脚通道、总压力/GRF 是否能导出？
4. 是否需要伦理审批或知情同意？
5. 您觉得这个方向适不适合作为 Sensors 投稿路线？

我可以先整理一个 1 页实验方案给您看。
```

### 11.4 汇报时不要过度承诺

不要说：

> 我们已经证明模型可以临床诊断 PD。

应该说：

> 我们已经完成了公开数据上的可复现 baseline，并正在设计实验室传感器数据验证，以评估模型和特征在真实采集条件下的可迁移性。

### 11.5 如果马老师问“你现在懂了吗”

你可以说：

> 我现在已经能讲清楚数据来源、任务定义、subject-level split、baseline 结果和下一步实验设计。模型内部数学细节我还在补，但这不影响目前推进数据采集和论文实验框架。

这是真实、稳妥、可信的回答。

## 12. 实验室数据采集最小方案

### 12.1 最低可行方案

人群：

- 健康志愿者 5-10 人。

任务：

- 正常速度步行。
- 每人 3 次。
- 每次 30 秒。
- 每次之间休息 1-2 分钟。

记录：

- subject_id。
- age。
- sex。
- height。
- weight。
- dominant leg。
- footwear。
- walking condition。
- trial number。
- sampling frequency。
- sensor model。

输出：

- 原始 sensor time series。
- 每个 trial 一个文件。
- 文件名包含 subject 和 trial。

用途：

- 检查数据读取。
- 检查特征提取。
- 检查健康人是否更接近 public control。
- 检查模型 false positive。

局限：

- 不能证明 PD classifier 外部泛化。
- 只能称为 feasibility / sanity validation。

### 12.2 更强方案

人群：

- 健康对照 10-20 人。
- 步态异常或相关疾病受试者 10-20 人。

如果能采 PD 最好。

如果不能采 PD，可以考虑：

- 膝骨关节炎。
- 术后康复。
- 跌倒风险老人。
- 神经系统疾病。

但要注意：

- 如果疾病不同，论文问题可能要调整。
- 不能把 OA 或术后患者直接说成 PD external validation。
- 可以改成 abnormal gait detection 或 sensor-domain validation。

### 12.3 最想问马老师的设备信息

必须确认：

- 设备品牌和型号。
- 传感器类型。
- 输出单位。
- 采样率。
- 是否分左右脚。
- 是否有总压力/总 GRF。
- 每个 sensor 的空间位置。
- 是否可以导出原始数据。
- 是否可以批量导出。
- 是否有厂家软件处理后的参数。

如果设备只能导出 summary，不导出原始 time series，项目仍然能做，但方法要调整。

## 13. 论文实验设计草案

### Exp 1：Classical ML model comparison

目的：

- 比较常用 classical ML 模型。
- 选择性能稳定的 baseline。

模型：

- Logistic Regression
- SVM-RBF
- KNN
- Random Forest
- Extra Trees
- Gradient Boosting
- XGBoost

验证：

- 5x5 repeated StratifiedGroupKFold。
- group = subject_id。

主指标：

- balanced accuracy。
- macro-F1。
- ROC-AUC。

### Exp 2：Feature selection

目的：

- 减少冗余特征。
- 找出关键 gait feature groups。

方法：

- mutual information filter。
- L1 logistic regression。
- tree-based importance。
- recursive feature elimination。

输出：

- 不同 feature 数量下的性能。
- selected feature list。

### Exp 3：Feature ablation

目的：

- 看哪类特征最重要。

分组：

- sensor-level statistics。
- total force statistics。
- left-right symmetry。
- contact/stance/swing。
- temporal derivative。

输出：

- 去掉某组特征后 balanced accuracy 下降多少。

### Exp 4：Raw time-series baseline

目的：

- 和手工特征 ML 对比。
- 看深度学习是否能直接从时间序列学到模式。

候选：

- 1D-CNN。
- LSTM/GRU。
- CNN-LSTM。

注意：

- 样本量只有 279 trials，深度学习很容易过拟合。
- 不能为了深度学习而深度学习。
- 如果深度学习不如 SVM/RF，也可以作为合理结果写入论文。

### Exp 5：Lab sensor validation

目的：

- 评估公开数据模型/特征在实验室传感器数据中的可用性。

根据实际采集情况分三档：

强：

- 实验室有 healthy + PD。
- 做 external validation。

中：

- 实验室有 healthy + other abnormal gait。
- 做 abnormal gait feasibility 或 transfer analysis。

弱：

- 实验室只有 healthy。
- 做 healthy external sanity check。

## 14. 论文结构草案

### Title 方向

候选：

```text
Subject-Level Machine Learning Classification of Parkinsonian Gait Using Ground Reaction Force Time-Series Features with Laboratory Sensor Validation
```

或：

```text
A Reproducible Machine Learning Pipeline for Parkinsonian Gait Classification Using Public Ground Reaction Force Data and Laboratory Sensor Validation
```

### Abstract

包括：

- Background：步态异常和传感器评估价值。
- Objective：建立可复现 ML pipeline。
- Methods：PhysioNet gaitpdb、feature extraction、subject-level CV、model comparison、lab validation。
- Results：SVM/RF 指标。
- Conclusion：可行性、关键特征、局限。

### Introduction

要讲：

- 步态是 PD/运动障碍的重要表型。
- 传统临床评估主观、低频。
- 传感器和 wearable devices 提供连续客观数据。
- ML 可从复杂 gait signals 中提取模式。
- 现有研究常见问题：数据集小、验证不严、外部验证不足。
- 本研究贡献。

### Methods

要讲：

- Dataset。
- File parsing。
- Exclusion of dual-task trials。
- Feature extraction。
- Models。
- Cross-validation。
- Metrics。
- Lab validation protocol。

### Results

要讲：

- 数据集统计。
- RF baseline。
- 模型对比。
- 特征重要性。
- feature selection / ablation。
- lab validation。

### Discussion

要讲：

- 为什么 SVM/RF 表现较好。
- 哪些特征可能反映 PD gait。
- 和文献对比。
- subject-level validation 的重要性。
- lab validation 的意义。
- 局限性。
- 未来工作。

### Conclusion

要讲：

- 我们建立了一个可复现 pipeline。
- 在公开数据上获得合理表现。
- 实验室验证支持/初步支持真实采集可行性。
- 后续需要更大样本、多中心、真实临床人群验证。

## 15. 你每天怎么推进这个项目

### 每天 30 分钟版

适合忙的时候：

- 看 1 个结果文件。
- 读 1 篇文献的 abstract 和 methods。
- 记录 3 条 notebook。
- 问 Codex 一个具体问题。

### 每天 2 小时版

适合集中推进：

1. 复现一个脚本。
2. 看输出图和表。
3. 整理一段 Methods。
4. 精读一篇文献。
5. 更新 TODO。

### 每周固定产出

每周至少要有：

- 1 张新图。
- 1 个新表。
- 1 段论文文字。
- 1 个可复现实验结果。
- 1 次和马老师或合作者同步。

dry lab 项目最怕“看了很多，没有产物”。一定要每周留下可见产物。

## 16. 怎么和 Codex 合作

你可以把 Codex 当成：

- 代码执行助手。
- 数据分析助手。
- 论文结构助手。
- 文献表格助手。
- debug 助手。

但你要保持医学判断。

好的提问方式：

```text
请读取 results/model_comparison_summary.csv，帮我生成论文 Results 里的一张模型对比表，并解释 balanced accuracy 为什么是主指标。
```

```text
请检查 src/run_model_comparison.py 是否存在 subject leakage 风险。
```

```text
请根据 Zotero collection 步态ML_PubMed文献，帮我做一张文献精读表。
```

```text
请写一版发给马康老师的实验室采集方案，要求医学老师能看懂。
```

不好的提问方式：

```text
帮我把论文做完。
```

原因：太大，无法验证质量。

## 17. 风险清单

### 17.1 数据集和最初设想不完全一致

最初手册里写过健康人 + 帕金森 + 中风、CSV。

实际：

- 没有中风。
- 是 PD vs control。
- 是 whitespace `.txt` time series。

应对：

- 论文方向改成 PD gait classification。
- 不再声称 stroke。

### 17.2 样本量不大

当前：

- 165 subjects。
- 279 normal-walk trials。

应对：

- 使用 repeated CV。
- 按 subject 分组。
- 报告均值和标准差。
- 不夸大结论。

### 17.3 Lab data 可能不够强

如果只采 healthy：

- 不能作为完整 external validation。
- 只能作为 feasibility validation。

应对：

- 论文语言保守。
- 尽量争取异常步态或患者数据。

### 17.4 设备 domain shift

公开数据可能是 force platform / foot sensors。

实验室设备可能是：

- 压力地板。
- 鞋垫。
- IMU。
- 跑步机。
- motion capture。

不同设备的信号不能直接等价。

应对：

- 先确认设备输出。
- 尽量设计共同特征，例如 gait cycle timing、左右对称性、总压力趋势。
- 不能直接比较的地方就不硬比。

### 17.5 过拟合

尤其是 1D-CNN/LSTM。

应对：

- 严格 subject-level split。
- 报告 repeated CV。
- 加 baseline 对照。
- 不因深度学习模型复杂就默认更好。

### 17.6 伦理和隐私

实验室采集人体数据，哪怕健康人，也可能需要：

- 知情同意。
- 去标识化。
- 伦理审批或备案。

应对：

- 尽快问马老师。
- 数据文件只用 subject_id，不存姓名、手机号、身份证。

## 18. 下一步最建议的实际行动

### 行动 1：今天联系马老师

这是最高优先级。

你不需要等模型更复杂。项目现在最需要确认的是 lab data 能不能落地。

### 行动 2：让我生成实验室采集方案

下一份文档建议写：

```text
docs/实验室步态数据采集方案.md
```

内容包括：

- 研究目的。
- 设备要求。
- 受试者要求。
- 采集流程。
- 文件命名。
- 数据字段。
- 伦理和隐私。
- 给马老师看的 1 页简版。

### 行动 3：做论文结果表格

从：

- `results/rf_baseline_metrics.csv`
- `results/model_comparison_summary.csv`

生成：

- Table 1: Dataset summary。
- Table 2: Model comparison。
- Figure 1: Pipeline diagram。
- Figure 2: Model balanced accuracy。
- Figure 3: Confusion matrix。
- Figure 4: Feature importance。

### 行动 4：文献精读

先精读 Zotero collection 里的 8 篇，不要一开始无限扩文献。

每篇只抓：

- 研究问题。
- 数据。
- 传感器。
- 模型。
- 验证。
- 指标。
- 对我们有什么用。

### 行动 5：补 feature selection / ablation

这是 Sensors 应用型 ML 论文很需要的部分。

## 19. 你的阶段性学习路线

### 第 1 周：会讲项目

目标：

- 能向马老师讲清楚项目为什么可行。
- 能讲清楚当前结果。
- 能提出实验室采集需求。

学习：

- ML 基本词汇。
- metrics。
- subject-level split。
- 项目文件结构。

### 第 2-4 周：会看结果

目标：

- 能看懂模型对比表。
- 能解释 confusion matrix。
- 能判断实验结果是否合理。
- 能协助写 Methods 和 Results。

学习：

- pandas 基础。
- sklearn workflow。
- cross-validation。
- feature importance。

### 第 2 个月：会设计实验

目标：

- 能提出 feature selection、ablation、external validation 方案。
- 能判断实验室数据能支持什么结论。

学习：

- 常见 ML 模型。
- 数据泄漏。
- 统计汇报。
- 论文图表。

### 第 3-6 个月：会写和答辩

目标：

- 能写 Introduction 和 Discussion。
- 能回答审稿人关于数据、验证、泛化、临床意义的质疑。

学习：

- 文献比较。
- 论文结构。
- limitation 写法。
- response letter 写法。

## 20. 你最应该记住的 10 句话

1. 我们做的是 PD vs healthy control，不是 stroke。
2. 原始数据是 time series，不是普通 CSV 表格。
3. 同一个 subject 不能同时进入 train 和 test。
4. balanced accuracy 比单纯 accuracy 更适合作为主指标。
5. baseline 不是终点，而是证明 pipeline 可行。
6. SVM-RBF 当前 subject-level CV 表现最好。
7. 实验室只采健康人不能证明 PD classifier 外部泛化。
8. 实验室验证的强弱取决于设备、标签、人群是否匹配。
9. 论文要讲临床问题、方法严谨性和传感器验证，不要只讲模型分数。
10. 你现在已经可以向马老师做第一次汇报。

## 21. 附录：常用复现命令

Windows PowerShell：

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

下载数据：

```powershell
.\.venv\Scripts\python.exe src\download_gaitpdb.py
```

如果需要代理：

```powershell
.\.venv\Scripts\python.exe src\download_gaitpdb.py --proxy http://127.0.0.1:7890
```

复跑 RF baseline：

```powershell
.\.venv\Scripts\python.exe src\run_rf_baseline.py --reuse-features
```

复跑模型对比：

```powershell
.\.venv\Scripts\python.exe src\run_model_comparison.py
```

查看 git 状态：

```powershell
git status --short
```

## 22. 附录：当前重要文件

项目说明：

- `README.md`
- `AGENTS.md`
- `docs/WINDOWS_CODEX_HANDOFF.md`
- `skills/gait-ml-paper/SKILL.md`

代码：

- `src/download_gaitpdb.py`
- `src/run_rf_baseline.py`
- `src/run_model_comparison.py`

数据：

- `data/gaitpdb/README.md`
- `data/processed/gaitpdb_features.csv`

结果：

- `results/rf_baseline_metrics.csv`
- `results/rf_baseline_classification_report.txt`
- `results/rf_baseline_confusion_matrix.png`
- `results/rf_baseline_feature_importance.csv`
- `results/rf_baseline_feature_importance_top25.png`
- `results/model_comparison_cv_results.csv`
- `results/model_comparison_summary.csv`
- `results/model_comparison_summary.json`
- `results/model_comparison_balanced_accuracy.png`

文献：

- `步态ML_PubMed文献.ris`
- Zotero collection：`步态ML_PubMed文献`

## 23. 最后的路线判断

这条路是可以走的。

但要把它走成论文，有两个关键：

1. 工程上守住 reproducibility 和 no leakage。
2. 医学上守住问题定义、验证边界和结论强度。

你现在不需要马上成为“懂所有算法的人”。你最该成为的是：

> 能提出正确临床问题、能识别错误验证方式、能把机器学习结果翻译成医学论文语言的人。

代码部分可以由 Codex 协助完成；但研究判断、实验室沟通、临床意义和论文边界，需要你来掌舵。

下一步：尽快联系马康老师，确认实验室数据采集条件。
