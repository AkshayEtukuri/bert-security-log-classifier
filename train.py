"""
Steps 2-4 -- Preprocessing, Fine-tuning, Evaluation for BERT Security Log Classifier.

Run:
    python train.py

Requires: torch, transformers, scikit-learn, pandas, matplotlib
(pip install -r requirements.txt)

Output:
    model/best_model/           -- saved fine-tuned model + tokenizer
    training_loss.png           -- loss curve
    confusion_matrix.png        -- confusion matrix on test set
"""

import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader
from torch.optim import AdamW
from transformers import AutoTokenizer, AutoModelForSequenceClassification, get_linear_schedule_with_warmup
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix
import matplotlib.pyplot as plt
import numpy as np

MODEL_NAME = "bert-base-uncased"
MAX_LEN = 128
BATCH_SIZE = 8
EPOCHS = 3
LR = 2e-5
LABEL_NAMES = ["normal", "suspicious", "malicious"]

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")


# ---------- Step 2: Preprocessing ----------
class LogDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_len=MAX_LEN):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        enc = self.tokenizer(
            self.texts[idx],
            truncation=True,
            padding="max_length",
            max_length=self.max_len,
            return_tensors="pt",
        )
        return {
            "input_ids": enc["input_ids"].squeeze(0),
            "attention_mask": enc["attention_mask"].squeeze(0),
            "labels": torch.tensor(self.labels[idx], dtype=torch.long),
        }


def load_data(path="data/security_logs.csv"):
    df = pd.read_csv(path)
    train_df, temp_df = train_test_split(df, test_size=0.2, stratify=df["label"], random_state=42)
    val_df, test_df = train_test_split(temp_df, test_size=0.5, stratify=temp_df["label"], random_state=42)
    return train_df.reset_index(drop=True), val_df.reset_index(drop=True), test_df.reset_index(drop=True)


# ---------- Step 3: Fine-tune BERT ----------
def train():
    train_df, val_df, test_df = load_data()
    print(f"Train: {len(train_df)}  Val: {len(val_df)}  Test: {len(test_df)}")

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=3).to(device)

    train_ds = LogDataset(train_df["text"].tolist(), train_df["label"].tolist(), tokenizer)
    val_ds = LogDataset(val_df["text"].tolist(), val_df["label"].tolist(), tokenizer)
    test_ds = LogDataset(test_df["text"].tolist(), test_df["label"].tolist(), tokenizer)

    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=BATCH_SIZE)
    test_loader = DataLoader(test_ds, batch_size=BATCH_SIZE)

    optimizer = AdamW(model.parameters(), lr=LR)
    total_steps = len(train_loader) * EPOCHS
    scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=0, num_training_steps=total_steps)

    train_losses = []
    best_val_f1 = 0.0

    for epoch in range(EPOCHS):
        model.train()
        epoch_loss = 0.0
        for batch in train_loader:
            optimizer.zero_grad()
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)

            outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
            loss = outputs.loss
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            scheduler.step()
            epoch_loss += loss.item()

        avg_loss = epoch_loss / len(train_loader)
        train_losses.append(avg_loss)

        # ---------- Step 4: Evaluate (per epoch on val set) ----------
        val_acc, val_f1, _, _ = evaluate(model, val_loader)
        print(f"Epoch {epoch+1}/{EPOCHS}  train_loss={avg_loss:.4f}  val_acc={val_acc:.4f}  val_f1={val_f1:.4f}")

        if val_f1 > best_val_f1:
            best_val_f1 = val_f1
            model.save_pretrained("model/best_model")
            tokenizer.save_pretrained("model/best_model")
            print(f"  -> saved new best model (val_f1={val_f1:.4f})")

    # Final test-set evaluation with the best checkpoint
    best_model = AutoModelForSequenceClassification.from_pretrained("model/best_model").to(device)
    test_acc, test_f1, y_true, y_pred = evaluate(best_model, test_loader)
    print(f"\nTest accuracy: {test_acc:.4f}  Test F1 (macro): {test_f1:.4f}")
    print("\nClassification report:")
    print(classification_report(y_true, y_pred, target_names=LABEL_NAMES))

    plot_loss(train_losses)
    plot_confusion_matrix(y_true, y_pred)


def evaluate(model, loader):
    model.eval()
    y_true, y_pred = [], []
    with torch.no_grad():
        for batch in loader:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)
            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            preds = torch.argmax(outputs.logits, dim=1)
            y_true.extend(labels.cpu().tolist())
            y_pred.extend(preds.cpu().tolist())
    acc = accuracy_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred, average="macro")
    return acc, f1, y_true, y_pred


def plot_loss(losses):
    plt.figure(figsize=(6, 4))
    plt.plot(range(1, len(losses) + 1), losses, marker="o")
    plt.xlabel("Epoch")
    plt.ylabel("Training Loss")
    plt.title("BERT Fine-tuning Loss Curve")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig("training_loss.png", dpi=150)
    print("Saved training_loss.png")


def plot_confusion_matrix(y_true, y_pred):
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(5, 4))
    plt.imshow(cm, cmap="Blues")
    plt.colorbar()
    plt.xticks(range(3), LABEL_NAMES, rotation=45)
    plt.yticks(range(3), LABEL_NAMES)
    for i in range(3):
        for j in range(3):
            plt.text(j, i, cm[i, j], ha="center", va="center",
                      color="white" if cm[i, j] > cm.max() / 2 else "black")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.title("Confusion Matrix (Test Set)")
    plt.tight_layout()
    plt.savefig("confusion_matrix.png", dpi=150)
    print("Saved confusion_matrix.png")


if __name__ == "__main__":
    train()
