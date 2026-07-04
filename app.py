"""
Step 5 -- Gradio UI for BERT Security Log Classifier.
Step 6 -- This file is also what you deploy to HuggingFace Spaces
          (SDK=Gradio, entry point app.py).

Local run:
    python app.py
Then open the local URL Gradio prints (usually http://127.0.0.1:7860)

For HuggingFace Spaces deployment:
    1. Create a new Space at huggingface.co/new-space, SDK = Gradio
    2. Upload: app.py, requirements.txt, and the model/best_model/ folder
       (or push the model to the HF Hub separately and load it by repo id
       instead of a local path -- recommended, keeps the Space repo small)
    3. Space auto-builds and serves this file
"""

import gradio as gr
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

MODEL_PATH = "model/best_model"  # swap for your HF Hub repo id once pushed, e.g. "AkshayEtukuri/bert-security-log-classifier"
LABEL_NAMES = ["normal", "suspicious", "malicious"]

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH).to(device)
model.eval()


def predict(log_text):
    if not log_text or not log_text.strip():
        return {name: 0.0 for name in LABEL_NAMES}
    enc = tokenizer(log_text, truncation=True, padding="max_length", max_length=128, return_tensors="pt").to(device)
    with torch.no_grad():
        logits = model(**enc).logits
        probs = torch.softmax(logits, dim=1).squeeze(0).cpu().tolist()
    return {LABEL_NAMES[i]: float(probs[i]) for i in range(len(LABEL_NAMES))}


EXAMPLES = [
    "[2026-07-20 14:32:01] INFO web-prod-01 user=jsmith action=login status=success src_ip=10.0.4.22",
    "[2026-07-20 03:14:55] WARN vpn-gw01 unusual login time detected user=admin hour=3 src_ip=10.0.2.10",
    "[2026-07-20 09:01:12] ALERT db-prod-02 SQL injection payload detected in request param='id' src_ip=185.22.14.9 payload_pattern=\"' OR 1=1--\" action=blocked",
]

demo = gr.Interface(
    fn=predict,
    inputs=gr.Textbox(lines=3, placeholder="Paste a security log line here...", label="Security Log Entry"),
    outputs=gr.Label(num_top_classes=3, label="Prediction"),
    examples=EXAMPLES,
    title="BERT Security Log Classifier",
    description="Fine-tuned BERT (bert-base-uncased) that classifies security log entries as normal, suspicious, or malicious.",
)

if __name__ == "__main__":
    demo.launch()
