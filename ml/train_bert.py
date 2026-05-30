"""
Entraînement BERT — Fine-tuning pour la détection de Fake News
Projet IA & Big Data L3 — Membre 2 (ML Engineer)

Usage:
    python train_bert.py --data_path ./data/processed --output ./models/bert-fakenews
    
Recommandé sur Google Colab (GPU T4 / A100)
"""
import os
import argparse
import logging
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.metrics import (
    accuracy_score, f1_score, classification_report, confusion_matrix
)
import torch
from torch.utils.data import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
    EarlyStoppingCallback,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL_NAME   = "bert-base-uncased"
NUM_LABELS   = 2
MAX_LENGTH   = 512
LABEL2ID     = {"FAKE": 0, "REAL": 1}
ID2LABEL     = {0: "FAKE", 1: "REAL"}


# ── Dataset ───────────────────────────────────────────────────────────────────
class FakeNewsDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_length=MAX_LENGTH):
        self.encodings = tokenizer(
            texts,
            truncation=True,
            padding="max_length",
            max_length=max_length,
            return_tensors="pt",
        )
        self.labels = labels

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        item = {k: v[idx] for k, v in self.encodings.items()}
        item["labels"] = torch.tensor(self.labels[idx], dtype=torch.long)
        return item


# ── Metrics ───────────────────────────────────────────────────────────────────
def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    return {
        "accuracy": accuracy_score(labels, predictions),
        "f1":       f1_score(labels, predictions, average="weighted"),
        "f1_fake":  f1_score(labels, predictions, average=None)[0],
        "f1_real":  f1_score(labels, predictions, average=None)[1],
    }


# ── Load data from Parquet (output of Spark pipeline) ─────────────────────────
def load_data(data_path: str):
    logger.info(f"Loading data from {data_path}")
    try:
        import pyarrow.parquet as pq
        # Lire directement les dossiers Parquet générés par Spark
        train_df = pd.read_parquet(f"{data_path}/train/")
        val_df   = pd.read_parquet(f"{data_path}/val/")
        test_df  = pd.read_parquet(f"{data_path}/test/")
    except Exception:
        # Fallback: load from CSV si Parquet non disponible
        logger.warning("Parquet not found. Loading from CSV...")
        df_fake = pd.read_csv("data/Fake.csv").assign(label=0, label_str="FAKE")
        df_real = pd.read_csv("data/True.csv").assign(label=1, label_str="REAL")
        df = pd.concat([df_fake, df_real]).dropna(subset=["text"]).reset_index(drop=True)
        df["content"] = df["title"].fillna("") + " [SEP] " + df["text"].fillna("")
        train_df = df.sample(frac=0.70, random_state=42)
        remaining = df.drop(train_df.index)
        val_df   = remaining.sample(frac=0.50, random_state=42)
        test_df  = remaining.drop(val_df.index)

    logger.info(f"Train: {len(train_df)} | Val: {len(val_df)} | Test: {len(test_df)}")
    return train_df, val_df, test_df


# ── Main training function ────────────────────────────────────────────────────
def train(args):
    # 1. Load tokenizer & model
    logger.info(f"Loading {MODEL_NAME}...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=NUM_LABELS,
        id2label=ID2LABEL,
        label2id=LABEL2ID,
    )

    # 2. Load data
    train_df, val_df, test_df = load_data(args.data_path)

    train_dataset = FakeNewsDataset(
        train_df["content"].tolist(),
        train_df["label"].tolist(),
        tokenizer,
    )
    val_dataset = FakeNewsDataset(
        val_df["content"].tolist(),
        val_df["label"].tolist(),
        tokenizer,
    )
    test_dataset = FakeNewsDataset(
        test_df["content"].tolist(),
        test_df["label"].tolist(),
        tokenizer,
    )

    # 3. Training arguments
    training_args = TrainingArguments(
        output_dir=args.output,
        num_train_epochs=3,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=32,
        learning_rate=2e-5,
        weight_decay=0.01,
        warmup_steps=500,
        logging_dir="./logs",
        logging_steps=100,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        greater_is_better=True,
        report_to="none",  # Set to "wandb" if using W&B
        fp16=torch.cuda.is_available(),
        dataloader_num_workers=4,
        seed=42,
    )

    # 4. Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        compute_metrics=compute_metrics,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=2)],
    )

    # 5. Train
    logger.info("🚀 Starting training...")
    trainer.train()

    # 6. Evaluate on test set
    logger.info("📊 Evaluating on test set...")
    test_results = trainer.evaluate(test_dataset)
    logger.info(f"Test results: {test_results}")

    predictions = trainer.predict(test_dataset)
    y_pred = np.argmax(predictions.predictions, axis=-1)
    y_true = test_df["label"].tolist()

    print("\n" + "="*60)
    print("CLASSIFICATION REPORT (Test Set)")
    print("="*60)
    print(classification_report(y_true, y_pred, target_names=["FAKE", "REAL"]))
    print("Confusion Matrix:")
    print(confusion_matrix(y_true, y_pred))
    print("="*60)

    # 7. Save model
    logger.info(f"💾 Saving model to {args.output}...")
    trainer.save_model(args.output)
    tokenizer.save_pretrained(args.output)
    logger.info("✅ Model saved successfully!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_path", type=str, default="./data/processed")
    parser.add_argument("--output",    type=str, default="./models/bert-fakenews")
    args = parser.parse_args()
    train(args)
