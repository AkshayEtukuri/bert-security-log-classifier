# 🧠 BERT Security Log Classifier

> Fine-tuning BERT for intelligent classification of cybersecurity logs into normal, suspicious, and malicious categories.

![Status](https://img.shields.io/badge/Status-In%20Progress-yellow?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)
![HuggingFace](https://img.shields.io/badge/HuggingFace-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black)
![Gradio](https://img.shields.io/badge/Gradio-FF7C00?style=for-the-badge&logo=gradio&logoColor=white)

---

## 📌 Overview

This project fine-tunes **BERT (bert-base-uncased)** to classify cybersecurity log entries into three threat categories. Rather than using keyword-based rule engines, this system learns contextual patterns in log text — making it more robust against obfuscated or edge-case attack signatures.

The project uses a **custom-built synthetic dataset** (v2) designed with realistic difficulty — overlapping vocabulary across classes and deliberate label noise — to ensure the model learns genuine patterns rather than trivial keyword shortcuts.

---

## 🎯 Problem Statement

Security operations teams deal with massive volumes of log data daily. Manual analysis is slow and error-prone. This classifier automates the triage process by labeling each log entry as:

| Label | Description |
|---|---|
| `normal` | Routine, expected system activity |
| `suspicious` | Anomalous patterns worth investigating |
| `malicious` | Clear indicators of attack or compromise |

---

## 🗂️ Dataset

Custom synthetic dataset built from scratch using a Python generator (`generate_dataset.py`) — not sourced from Kaggle or any external platform.

| Property | Details |
|---|---|
| **Version** | v2 (corrected — realistic difficulty) |
| **Total Rows** | 3,600 |
| **Class Distribution** | normal: 1201 / suspicious: 1201 / malicious: 1198 |
| **Split** | 80% train / 10% val / 10% test (stratified) |
| **Label Noise** | ~5% deliberate noise injected |
| **Vocabulary** | Overlapping terms across classes |

> **Why custom dataset?** v1 of the dataset was trivially solvable by keyword matching, producing a meaningless 100% accuracy. v2 was rebuilt with overlapping vocabulary and label noise to ensure the model learns genuine contextual patterns.

---

## 🏗️ Model Architecture

```
Input Log Text
      ↓
BERT Tokenizer (bert-base-uncased, max_length=128)
      ↓
BERT Encoder (12 transformer layers)
      ↓
[CLS] Token Representation
      ↓
Classification Head (Linear → 3 classes)
      ↓
Output: normal / suspicious / malicious
```

---

## ⚙️ Training Configuration

| Parameter | Value |
|---|---|
| **Base Model** | bert-base-uncased |
| **Task** | Sequence Classification (3 classes) |
| **Max Sequence Length** | 128 tokens |
| **Epochs** | 3 |
| **Batch Size** | 8 |
| **Optimizer** | AdamW |
| **Learning Rate** | 2e-5 |
| **Scheduler** | Linear warmup |

---

## 🛠️ Tech Stack

| Category | Tools |
|---|---|
| **Model** | HuggingFace Transformers (AutoModelForSequenceClassification) |
| **Tokenizer** | AutoTokenizer (bert-base-uncased) |
| **Training** | PyTorch, AdamW, linear warmup scheduler |
| **Evaluation** | scikit-learn (accuracy, F1, classification report, confusion matrix) |
| **Data** | pandas, custom Python generator |
| **Visualization** | matplotlib (loss curves, confusion matrix) |
| **Demo UI** | Gradio (app.py) |

---

## 📁 Project Structure

```
bert-security-log-classifier/
│
├── generate_dataset.py      # Custom synthetic dataset generator
├── dataset_v2.csv           # Generated dataset (v2)
├── train.py                 # BERT fine-tuning training loop
├── evaluate.py              # Model evaluation & metrics
├── app.py                   # Gradio demo UI
├── requirements.txt         # Dependencies
├── outputs/
│   ├── loss_curve.png       # Training & validation loss plot
│   └── confusion_matrix.png # Confusion matrix visualization
└── README.md
```

---

## 📊 Results

> ⏳ **Training in progress** on v2 dataset. Results will be updated once training completes.

| Metric | Score |
|---|---|
| **Accuracy** | TBD |
| **F1 Score (macro)** | TBD |
| **val Loss** | TBD |

> Note: v1 achieved 100% accuracy on an oversimplified dataset. v2 was rebuilt with realistic difficulty to produce meaningful evaluation metrics.

---

## 🚀 How to Run

### 1. Install Dependencies
```bash
pip install torch transformers scikit-learn pandas matplotlib gradio
```

### 2. Generate Dataset
```bash
python generate_dataset.py
```

### 3. Train the Model
```bash
python train.py
```

### 4. Evaluate
```bash
python evaluate.py
```

### 5. Launch Gradio Demo
```bash
python app.py
```

---

## 🔮 Future Improvements

- [ ] Update results after v2 training completes
- [ ] Experiment with DistilBERT for faster inference
- [ ] Add real-world log samples (CICIDS, UNSW-NB15)
- [ ] Deploy Gradio demo to HuggingFace Spaces
- [ ] Add SHAP explainability for model decisions

---

## 🔗 Related Projects

- [KDD Cup 99 — Network Intrusion Detection](https://github.com/AkshayEtukuri/KDD-Intrusion-Detection) — Classical ML approach to network security
- AI-IDS Capstone *(coming soon)* — End-to-end intelligent intrusion detection system

---

## 👤 Author

**Akshay Etukuri**
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat&logo=linkedin&logoColor=white)](https://linkedin.com/in/akshay-etukuri-054a15207/)
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=flat&logo=github&logoColor=white)](https://github.com/AkshayEtukuri)

---

*Part of an ongoing AI/ML portfolio focused on intelligent cybersecurity systems.*
