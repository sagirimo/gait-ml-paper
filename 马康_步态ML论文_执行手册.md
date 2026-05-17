# 步态 ML 论文 — 执行手册

**目标期刊**: Sensors (MDPI, IF 3.4, 审稿 4-6 周, Open Access)
**方向**: 公开步态数据集 + ML 对比实验 + 实验室传感器验证

---

## Sensors 是啥
- MDPI 旗下开放获取期刊，CiteScore 7.3
- 收：传感器、可穿戴设备、信号处理、ML 应用
- 特点：**审稿快**（4-6 周）、不要求 State-of-the-art 创新、方法学扎实就行
- 版面费 ~$2,000（确认前问马康能不能走课题经费）

---

## Phase 1：启动（今天 — 5.17）

### Step 1: 下载数据集（今晚）
1. 打开 https://physionet.org/content/gaitpdb/1.0.0/
2. 下载 CSV 文件（健康人 + 帕金森 + 中风步态）
3. 看看列：时间戳、左脚压力、右脚压力、步幅、步频等

### Step 2: 跑 baseline（明天）
```python
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split from sklearn.metrics import classification_report

df = pd.read_csv("gait_data.csv")
X = df.drop(["label"], axis=1)  # 特征
y = df["label"]                 # 标签（健康/异常）

X_train, X_test, y_train, y_test = train_test_split(X, y)
clf = RandomForestClassifier()
clf.fit(X_train, y_train)
print(classification_report(y_test, clf.predict(X_test)))
```
10 行代码，今晚跑完——你就有第一个 Baseline 结果。

### Step 3: 跟马康确认验证数据（明天）
> 马老师，我下了 PhysioNet 公开步态数据做训练。能不能借用实验室压力地板/跑步机，帮我采 5-10 个健康人的步态数据做验证？一个人走 3 次，一次 30 秒，一个下午收完。

---

## Phase 2：实验（5.18 — 6.15）

### 实验设计（4 组对比）
| 实验 | 做什么 | 证明什么 |
|------|--------|---------|
| Exp 1 | 5 种 ML 模型对比（RF, XGBoost, SVM, KNN, LR） | 模型选择有依据 |
| Exp 2 | 3 种特征筛选方法（Filter, Wrapper, Embedded） | 特征工程能力 |
| Exp 3 | 消融实验（去掉某类特征看影响） | 特征贡献可解释 |
| Exp 4 | 公开数据训练 → 实验室传感器数据验证 | 泛化能力 + 实用价值 |

### 每天做什么
- 跑一组实验，把准确率、F1、AUC 记进 Excel
- 画一张对比图（条形图/混淆矩阵）

---

## Phase 3：写论文（6.16 — 7.15）

### 论文结构（Sensors 模板）
1. **Introduction** — 步态评估为什么重要 + 现有方法局限 + 本文贡献（1 页）
2. **Related Work** — 步态 ML 综述（0.5 页）
3. **Methods** — 数据集 + 特征提取 + 模型 + 实验设计（2 页）
4. **Results** — 4 组实验结果表格 + 图表（1.5 页）
5. **Discussion** — 分析结果 + 局限性 + 临床意义（1 页）
6. **Conclusion** — 总结 + 未来工作（0.5 页）

总共 3000-4000 词，Sensors 的 Methods paper 格式。

### 写论文工具
- GPT：把实验结果表格贴进去 → "帮我把 Methods 部分写成 Sensors 格式，1500 词"
- 图表：Python matplotlib 画，GPT 帮你调代码

---

## Phase 4：投稿（7 月底）

1. Sensors 官网 https://www.mdpi.com/journal/sensors → Submit
2. 上传 Manuscript + Figures + Cover Letter
3. 4-6 周审稿
4. 修回 → 录用 → 10 月底前 published

---

## 关键里程碑
| 日期 | 目标 |
|------|------|
| 今晚 | 下载数据 + 看懂列 |
| 明天 | Baseline RF 跑通 |
| 5.17 | 跟马康确认验证数据 |
| 6.15 | 四组实验全跑完 |
| 7.15 | 论文初稿写完 |
| 7.31 | 投稿 |
| 10 月底 | Published |
