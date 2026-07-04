# BERT Security Log Classifier

Fine-tuned BERT (`bert-base-uncased`) that classifies security log entries into
**normal**, **suspicious**, or **malicious**, with a Gradio UI deployed on
HuggingFace Spaces.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![PyTorch](https://img.shields.io/badge/PyTorch-2.x-red)
![Transformers](https://img.shields.io/badge/HuggingFace-Transformers-yellow)
![Gradio](https://img.shields.io/badge/Gradio-UI-orange)

🔗 **Live demo:** [huggingface.co/spaces/EAkshay/bert-security-log-classifier](https://huggingface.co/spaces/EAkshay/bert-security-log-classifier)


📝 **Blog post:** [akshayetukuri.hashnode.dev/fine-tuning-bert-to-classify-security-logs-and-the-100-accuracy-trap-i-fell-into](https://akshayetukurihashnodedev.hashnode.dev/fine-tuning-bert-to-classify-security-logs-and-the-100-accuracy-trap-i-fell-into)


---

## Problem

Security teams triage huge volumes of raw log lines by hand or with brittle
regex rules. This project fine-tunes BERT to read a single log line and
classify it into three severity buckets, giving analysts a fast, learned
first pass instead of hardcoded pattern matching.

## Dataset

3-class security log dataset (`normal` / `suspicious` / `malicious`),
1,200 samples per class, format `text,label`. See `generate_dataset.py`
for the synthetic generator used here — swap in a real Kaggle security-log
dataset by producing a CSV in the same `text,label` format and pointing
`train.py` at it.

## Architecture

- **Base model:** `bert-base-uncased` (encoder-only, 12 layers, 110M params)
- **Head:** linear classification head, 3 output classes
- **Tokenizer:** WordPiece, max sequence length 128
- **Fine-tuning:** AdamW, lr=2e-5, linear warmup schedule, 3 epochs, batch size 8

## Results

| Metric | Score |
|---|---|
| Test Accuracy | 94.44% |
| Test Macro F1 | 0.9445 |

**Per-class breakdown (test set, 120 samples/class):**

| Class | Precision | Recall | F1 |
|---|---|---|---|
| normal | 0.97 | 0.93 | 0.94 |
| suspicious | 0.91 | 0.95 | 0.93 |
| malicious | 0.96 | 0.96 | 0.96 |

**Training config:** 3 epochs, batch size 8 (reduced from 16 due to local CPU/memory
constraints), learning rate 2e-5, max sequence length 128, AdamW + linear warmup.
Training loss dropped steadily across epochs (0.386 → 0.283 → 0.272) with no signs
of overfitting; validation accuracy converged by epoch 1 and held stable.

See `training_loss.png` and `confusion_matrix.png` for the full curve and per-class
breakdown.

### A note on dataset design (v1 → v2)

The first version of the synthetic dataset generator used disjoint vocabulary and a
consistent severity prefix (`INFO`/`WARN`/`ALERT`) that lined up 1:1 with the label.
That let the model hit a meaningless 100% test accuracy by memorizing surface
patterns rather than learning anything about log content. The generator was rebuilt
(v2) to share vocabulary across classes, randomize severity tags independently of the
label, include deliberately ambiguous borderline cases, and inject ~5% label noise —
which is realistic for hand-labeled security data. The 94.44% result above is from
the corrected v2 dataset, and the "suspicious" class (which sits between the other
two in both meaning and vocabulary overlap) is, as expected, the hardest to classify.

## Project structure

```
bert-security-log-classifier/
├── generate_dataset.py   # Step 1: synthetic dataset generator
├── train.py               # Steps 2-4: preprocessing, fine-tuning, evaluation
├── app.py                  # Step 5-6: Gradio UI / HF Spaces entry point
├── requirements.txt
├── data/
│   └── security_logs.csv
└── model/
    └── best_model/        # saved fine-tuned model + tokenizer (generated)
```

## Running locally

```bash
pip install -r requirements.txt
python generate_dataset.py   # or supply your own data/security_logs.csv
python train.py               # fine-tunes BERT, saves best checkpoint + plots
python app.py                  # launches Gradio UI at http://127.0.0.1:7860
```

## Deployment (HuggingFace Spaces)

1. Create a new Space at huggingface.co/new-space, SDK = **Gradio**
2. Push `app.py`, `requirements.txt`, and the `model/best_model/` folder
   (or push the model separately to the HF Hub and load it by repo id in
   `app.py` — recommended for keeping the Space repo lightweight)
3. Space auto-builds and serves `app.py`

## Author

Akshay Etukuri — [github.com/AkshayEtukuri](https://github.com/AkshayEtukuri)
