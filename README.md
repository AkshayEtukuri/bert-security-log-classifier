<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:1a1a2e,50:16213e,100:0f3460&height=200&section=header&text=BERT%20Security%20Log%20Classifier&fontSize=40&fontColor=00D4FF&animation=fadeIn&fontAlignY=38&desc=Teaching%20AI%20to%20Think%20Like%20a%20Security%20Analyst&descAlignY=55&descColor=ffffff" />

</div>

<div align="center">

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)
![HuggingFace](https://img.shields.io/badge/🤗_HuggingFace-FFD21E?style=for-the-badge)
![Gradio](https://img.shields.io/badge/Gradio-FF7C00?style=for-the-badge)
![BERT](https://img.shields.io/badge/BERT-base--uncased-00D4FF?style=for-the-badge)

<br/>

```
███████╗███████╗ ██████╗██╗   ██╗██████╗ ██╗████████╗██╗   ██╗
██╔════╝██╔════╝██╔════╝██║   ██║██╔══██╗██║╚══██╔══╝╚██╗ ██╔╝
███████╗█████╗  ██║     ██║   ██║██████╔╝██║   ██║    ╚████╔╝ 
╚════██║██╔══╝  ██║     ██║   ██║██╔══██╗██║   ██║     ╚██╔╝  
███████║███████╗╚██████╗╚██████╔╝██║  ██║██║   ██║      ██║   
╚══════╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝   ╚═╝      ╚═╝  
```

*"Not every threat announces itself. Some whisper."*

</div>

---

## 🔴 THREAT INCOMING...

```bash
$ tail -f /var/log/system.log

[2024-01-15 03:42:17] auth: Failed login attempt from 192.168.1.105
[2024-01-15 03:42:18] auth: Failed login attempt from 192.168.1.105  
[2024-01-15 03:42:19] auth: Failed login attempt from 192.168.1.105
[2024-01-15 03:42:20] ssh: Connection established from 192.168.1.105
[2024-01-15 03:42:21] sys: Privilege escalation detected — root access

>>> BERT CLASSIFIER ACTIVATED...
>>> Analyzing log pattern...
>>> Contextual embedding generated...
>>> Classification: ⚠️  MALICIOUS  [confidence: 97.3%]
>>> Alert dispatched to SOC team.
```

*This is what this project does — in real time.*

---

## 🧠 The Idea

Every second, servers generate thousands of log lines. Most are boring.
Some are suspicious. A few are dangerous.

The old way? Rules. Keywords. Static filters.
If attacker changes one word — the rule misses it.

**The new way? Context.**

BERT reads a log entry the way a human analyst would — understanding
the *meaning* behind the words, not just matching patterns.

```
Rule Engine:  "failed login" → suspicious ✓
              "unsuccessful authentication" → ??? ✗ missed

BERT:         "unsuccessful authentication" → suspicious ✓ caught
              (because it understands language, not just keywords)
```

---

## 🎯 What It Classifies

<div align="center">

| 🟢 NORMAL | 🟡 SUSPICIOUS | 🔴 MALICIOUS |
|:---:|:---:|:---:|
| Routine system activity | Anomalous patterns | Active attack signatures |
| Expected user behavior | Worth investigating | Immediate response needed |
| Healthy network traffic | Unusual access times | Privilege escalation |

</div>

---

## 🗂️ The Dataset — Built From Scratch

> No Kaggle. No shortcuts. Built a Python generator from zero.

```python
# generate_dataset.py — The data factory
$ python generate_dataset.py

✓ Generating normal logs...     [████████████████] 1201 rows
✓ Generating suspicious logs... [████████████████] 1201 rows  
✓ Generating malicious logs...  [████████████████] 1198 rows
✓ Injecting 5% label noise...   [████████████████] done
✓ Shuffling dataset...          [████████████████] done

Dataset v2 ready → 3,600 rows saved to dataset_v2.csv
```

### Why v2?

> v1 was too easy. BERT hit 100% accuracy — but that's not impressive,
> that's a red flag. The logs were trivially separable by keywords alone.
> 
> v2 fixes this with **overlapping vocabulary** and **deliberate noise**.
> Now the model actually has to *think*.

| | v1 Dataset | v2 Dataset |
|---|:---:|:---:|
| Vocabulary overlap | ❌ None | ✅ Intentional |
| Label noise | ❌ None | ✅ ~5% injected |
| Trivially solvable | ✅ Yes (bad) | ❌ No (good) |
| Accuracy meaning | ❌ Meaningless | ✅ Meaningful |

---

## 🏗️ Under The Hood

```
┌─────────────────────────────────────────────────────────┐
│                    INPUT LOG ENTRY                       │
│  "root login failed 47 times from unknown IP at 3AM"    │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│               BERT TOKENIZER                             │
│  [CLS] root login failed 47 times from unknown [SEP]    │
│  Token IDs: [101, 4903, 7592, 3659, 4737, ...]          │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│          BERT ENCODER (12 Transformer Layers)            │
│  Each token attends to every other token                 │
│  "failed" ←→ "47 times" ←→ "3AM" ←→ "unknown IP"       │
│  Context flows in both directions simultaneously         │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│            [CLS] TOKEN REPRESENTATION                    │
│  768-dimensional vector encoding full log meaning        │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│           CLASSIFICATION HEAD                            │
│  Linear(768 → 3) + Softmax                              │
│  normal: 1.2% | suspicious: 3.1% | malicious: 95.7%    │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
                  🔴 MALICIOUS
```

---

## ⚙️ Training Config

```python
config = {
    "model"        : "bert-base-uncased",
    "task"         : "SequenceClassification → 3 classes",
    "max_length"   : 128,       # tokens per log entry
    "epochs"       : 3,
    "batch_size"   : 8,         # CPU training on local machine
    "optimizer"    : "AdamW",
    "lr"           : 2e-5,      # standard BERT fine-tuning rate
    "scheduler"    : "linear warmup",
    "dataset"      : "custom v2 — 3,600 rows",
    "split"        : "80/10/10 stratified",
}
```

---

## 📊 Results

<div align="center">

```
⏳ Training in progress on v2 dataset...
   Results will be updated once training completes.
```

| Metric | Score |
|---|:---:|
| Accuracy | `updating...` |
| F1 Score (macro) | `updating...` |
| Val Loss | `updating...` |

> v1 achieved 100% — and that's exactly why we rebuilt the dataset.
> Real results coming soon.

</div>

---

## 🛠️ Tech Stack

```
Language        →  Python
Model           →  bert-base-uncased (HuggingFace Transformers)
Deep Learning   →  PyTorch
Tokenizer       →  AutoTokenizer
Classifier      →  AutoModelForSequenceClassification
Optimizer       →  AdamW + Linear Warmup Scheduler
Evaluation      →  scikit-learn (F1, accuracy, confusion matrix)
Data            →  pandas + custom generator
Visualization   →  matplotlib (loss curves, confusion matrix)
Demo            →  Gradio
```

---

## 📁 Project Structure

```
bert-security-log-classifier/
│
├── 📊 generate_dataset.py      ← builds synthetic log dataset
├── 📋 dataset_v2.csv           ← 3,600 labelled log entries
├── 🏋️ train.py                 ← fine-tuning loop
├── 📐 evaluate.py              ← metrics & evaluation
├── 🖥️ app.py                   ← Gradio live demo
├── 📦 requirements.txt
│
└── outputs/
    ├── 📈 loss_curve.png        ← training & val loss plot
    └── 🗺️ confusion_matrix.png  ← classification heatmap
```

---

## 🚀 Run It Yourself

```bash
# 1. Clone & install
git clone https://github.com/AkshayEtukuri/bert-security-log-classifier
pip install torch transformers scikit-learn pandas matplotlib gradio

# 2. Generate dataset
python generate_dataset.py

# 3. Train
python train.py

# 4. Evaluate
python evaluate.py

# 5. Launch demo
python app.py
# → opens at http://localhost:7860
```

---

## 🔮 What's Next

- [ ] Update results table after v2 training finishes
- [ ] Try DistilBERT — same accuracy, 60% faster
- [ ] Add real-world logs (CICIDS2017, UNSW-NB15)
- [ ] Deploy Gradio demo to HuggingFace Spaces
- [ ] Add SHAP explanations — *why* did BERT flag this log?
- [ ] Connect to AI-IDS Capstone as the NLP module

---

## 👤 Built By

<div align="center">

**Akshay Etukuri**
*AI/ML Engineer in the Making | Cybersecurity + Deep Learning*

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/akshay-etukuri-054a15207/)
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/AkshayEtukuri)
[![Portfolio](https://img.shields.io/badge/Portfolio-00D4FF?style=for-the-badge&logo=firefox&logoColor=white)](https://akshayetukuri.github.io)

</div>

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0f3460,50:16213e,100:1a1a2e&height=120&section=footer&text=Not%20every%20threat%20announces%20itself.&fontSize=20&fontColor=00D4FF&animation=fadeIn" />

</div>
