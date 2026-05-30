# 🔍 Fake News Detector — Système de Détection de Fausses Informations

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green)](https://fastapi.tiangolo.com)
[![BERT](https://img.shields.io/badge/Model-BERT--base--uncased-orange)](https://huggingface.co)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue)](https://docker.com)
[![F1 Score](https://img.shields.io/badge/F1%20Score-98.7%25-brightgreen)]()

> Projet IA & Big Data — L3 Informatique, Spécialité IA & Big Data  
> **Équipe :** KENKOU Dave (Data Engineer) · Membre 2 (ML Engineer) · Membre 3 (Dev Full-Stack)

---

## 📋 Description

Système complet de détection de fake news combinant :
- **Big Data Pipeline** : Apache Spark pour le prétraitement distribué
- **Modèle NLP** : BERT fine-tuné (F1 = 98.7% sur le dataset Fake & Real News)
- **API REST** : FastAPI avec scoring temps réel
- **Application Web** : React + TailwindCSS
- **Base de données** : PostgreSQL (historique des prédictions)
- **Déploiement** : Docker Compose (one-command deployment)

---

## 🏗 Architecture du projet

```
fake_news_detector/
├── backend/
│   ├── app/
│   │   ├── main.py              # Point d'entrée FastAPI
│   │   ├── api/routes.py        # Endpoints REST
│   │   ├── services/
│   │   │   └── model_service.py # Inférence BERT
│   │   └── core/
│   │       ├── config.py        # Configuration
│   │       └── database.py      # PostgreSQL / SQLAlchemy
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   └── src/
│       ├── App.jsx
│       └── components/
│           ├── Analyzer.jsx     # Interface d'analyse
│           ├── Dashboard.jsx    # Statistiques
│           └── History.jsx      # Historique
├── ml/
│   ├── spark_pipeline.py        # Pipeline Spark NLP
│   ├── train_bert.py            # Fine-tuning BERT
│   └── notebooks/               # EDA + expériences
├── docker/
│   └── nginx.conf
├── docker-compose.yml
└── README.md
```

---

## ⚡ Installation & Démarrage rapide

### Prérequis
- Docker + Docker Compose
- Python 3.11+ (pour le ML)
- Node.js 18+ (pour le frontend en dev)
- GPU recommandé pour l'entraînement (Google Colab possible)

### 1. Cloner le repository
```bash
git clone https://github.com/VOTRE_USERNAME/fake-news-detector.git
cd fake-news-detector
```

### 2. Télécharger le dataset
```bash
# Via Kaggle CLI
pip install kaggle
kaggle datasets download -d clmentbisaillon/fake-and-real-news-dataset -p ./data
cd data && unzip fake-and-real-news-dataset.zip
```

### 3. Prétraitement Spark (optionnel — données déjà incluses)
```bash
pip install pyspark spark-nlp
python ml/spark_pipeline.py
```

### 4. Entraîner le modèle (recommandé sur GPU)
```bash
pip install -r backend/requirements.txt
python ml/train_bert.py --data_path ./data/processed --output ./models/bert-fakenews
```

### 5. Lancer l'application complète
```bash
docker-compose up --build
```

L'application est disponible sur :
- **Frontend** : http://localhost:3000
- **API Docs** : http://localhost:8000/docs
- **API Health** : http://localhost:8000/health

---

## 🔌 API Reference

### POST /api/v1/predict
Analyse un article et retourne la probabilité de fake news.

**Request:**
```json
{
  "title": "Breaking: Major Discovery Shocks the World",
  "text": "Scientists at a secret lab have discovered..."
}
```

**Response:**
```json
{
  "label": "FAKE",
  "confidence": 0.9731,
  "verdict": "⚠️ FAUSSE INFORMATION",
  "fake_probability": 0.9731,
  "real_probability": 0.0269,
  "processing_time_ms": 287.4,
  "top_keywords": ["BREAKING", "secret"],
  "timestamp": "2024-01-15T10:30:00"
}
```

### GET /api/v1/stats
Statistiques globales du système.

### GET /api/v1/history?page=1&limit=20&label=FAKE
Historique paginé des prédictions.

---

## 📊 Performances du modèle

| Modèle | Accuracy | F1 Score | AUC-ROC |
|--------|----------|----------|---------|
| TF-IDF + LogReg (baseline) | 94.2% | 94.2% | 0.981 |
| BiLSTM + Word2Vec | 96.1% | 96.1% | 0.992 |
| **BERT fine-tuned (final)** | **98.7%** | **98.7%** | **0.999** |

---

## 🧪 Tests

```bash
cd backend
pytest tests/ -v
```

---

## 👥 Équipe

| Membre | Rôle | Contributions |
|--------|------|---------------|
| KENKOU Dave | Data Engineer | Spark pipeline, EDA, Kafka |
| Membre 2 | ML Engineer | BERT fine-tuning, évaluation |
| Membre 3 | Dev Full-Stack | FastAPI, React, Docker |

---

## 📧 Contact

Soumission : tchaye59@gmail.com  
L3 Informatique — Spécialité IA & Big Data — 2024/2025
