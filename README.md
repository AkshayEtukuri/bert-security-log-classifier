# BERT Security Log Classifier

Fine-tuned BERT (`bert-base-uncased`) that classifies security log entries into
**normal**, **suspicious**, or **malicious**, with a Gradio UI deployed on
HuggingFace Spaces.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![PyTorch](https://img.shields.io/badge/PyTorch-2.x-red)
![Transformers](https://img.shields.io/badge/HuggingFace-Transformers-yellow)
![Gradio](https://img.shields.io/badge/Gradio-UI-orange)

🔗 **Live demo:** [HuggingFace Spaces link — add after deployment]
📝 **Blog post:** [Hashnode link — add after publishing]

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
- **Fine-tuning:** AdamW, lr=2e-5, linear warmup schedule, 3 epochs, batch size 16

## Results

| Metric | Score |
|---|---|
| Test Accuracy | fill in after training run |
| Test Macro F1 | fill in after training run |

See `training_loss.png` and `confusion_matrix.png` for the training curve
and per-class breakdown.

## Project structure

```
bert-security/
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
