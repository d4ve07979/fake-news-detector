# FakeDetect — Système de Détection de Fake News à Grande Échelle

Projet académique L3 Informatique — Spécialité IA & Big Data
Encadrant : Dr. Tchaye

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)](https://reactjs.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)](https://docker.com)
[![HuggingFace](https://img.shields.io/badge/HuggingFace-XLM--RoBERTa-yellow)](https://huggingface.co)
[![Apache Spark](https://img.shields.io/badge/Apache-Spark-E25A1C?logo=apachespark)](https://spark.apache.org)

---

## Description

FakeDetect est un système complet de détection automatique de fake news combinant :

- **Big Data** : pipeline Apache Spark NLP traitant 44 898 articles
- **NLP / IA** : modèle XLM-RoBERTa fine-tuné (F1 = 99,9% sur test set)
- **Backend** : API REST FastAPI avec persistance SQLite/PostgreSQL
- **Frontend** : Application React avec 6 pages (Analyser, Dashboard, Batch, Historique...)
- **DevOps** : Déploiement Docker Compose en 4 services

---

## Architecture

```
CSV Bruts --> Spark NLP --> Parquet --> BERT/XLM-RoBERTa --> FastAPI --> React App
 Kaggle        Nettoyage    Big Data      Fine-tuning GPU       REST API    Interface
44,898 art.    Anti-biais   Optimise      F1 = 99.9%            <500ms      6 pages
```

### Services Docker

```
+---------------------------------------------+
|            docker-compose.yml               |
|  +----------+  +----------+  +----------+  |
|  |  nginx   |  | frontend |  |   api    |  |
|  |  :80     |  |  :3000   |  |  :8000   |  |
|  +----------+  +----------+  +----------+  |
|                              +----------+   |
|                              |    db    |   |
|                              |  :5432   |   |
|                              +----------+   |
+---------------------------------------------+
```

---

## Demarrage rapide

### Prerequis

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installe et demarre
- Modele entraine place dans `models/bert-fakenews/`

### Lancement en une commande

```bash
git clone https://github.com/d4ve07979/fake-news-detector.git
cd fake-news-detector
docker-compose up --build
```

L'application est accessible sur **http://localhost**

> Le dossier `models/bert-fakenews/` n'est pas inclus dans le repo (trop lourd ~1 Go).
> Voir la section Modele pour l'obtenir.

---

## Developpement local (sans Docker)

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac
pip install -r requirements.txt

# Creer la base de donnees
python -c "from app.core.database import init_db; init_db()"

# Lancer l'API
uvicorn app.main:app --port 8000 --reload
```

API disponible sur http://localhost:8000
Documentation Swagger sur http://localhost:8000/docs

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Interface disponible sur http://localhost:3000

---

## Modele

Le modele XLM-RoBERTa fine-tune n'est pas inclus dans ce depot Git (taille ~1 Go).

### Entrainer le modele (Google Colab recommande)

```bash
cd ml
# Etape 1 — Pipeline Spark NLP
python spark_pipeline.py

# Etape 2 — Entrainement BERT v2 (XLM-RoBERTa multilingue)
python train_bert_v2.py \
    --model xlm-roberta-base \
    --output ./bert-fakenews \
    --fake_csv data/Fake.csv \
    --real_csv data/True.csv
```

### Structure attendue du modele

```
models/
└── bert-fakenews/
    ├── config.json
    ├── model.safetensors
    ├── tokenizer.json
    ├── tokenizer_config.json
    └── training_args.bin
```

---



## Structure du projet

```
fake-news-detector/
├── backend/
│   ├── app/
│   │   ├── api/routes.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── database.py
│   │   ├── services/
│   │   │   └── model_service.py
│   │   └── main.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Analyzer.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── History.jsx
│   │   │   ├── Batch.jsx
│   │   │   ├── Landing.jsx
│   │   │   └── About.jsx
│   │   ├── App.jsx
│   │   └── app.css
│   ├── Dockerfile
│   └── package.json
│
├── ml/
│   ├── spark_pipeline.py
│   ├── train_bert_v2.py
│   ├── test_overfitting.py
│   └── evaluation/
│       └── compare_models.py
│
├── models/
│   └── .gitkeep
│
├── docker/
│   └── nginx.conf
│
├── docker-compose.yml
├── Makefile
└── README.md
```

---

## API Endpoints

| Endpoint | Methode | Description |
|----------|---------|-------------|
| `/health` | GET | Statut de l'API et du modele |
| `/api/v1/predict` | POST | Analyse d'un article unique |
| `/api/v1/batch` | POST | Analyse de plusieurs articles |
| `/api/v1/stats` | GET | Statistiques depuis la BDD |
| `/api/v1/history` | GET | Historique pagine des predictions |
| `/api/v1/history/{id}` | DELETE | Supprimer une prediction |

### Exemple de requete

```bash
curl -X POST http://localhost:8000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Federal Reserve holds interest rates steady",
    "text": "The Federal Reserve kept interest rates unchanged on Wednesday..."
  }'
```

### Exemple de reponse

```json
{
  "id": 1,
  "label": "REAL",
  "confidence": 0.9637,
  "verdict": "INFORMATION CREDIBLE",
  "fake_probability": 0.0363,
  "real_probability": 0.9637,
  "processing_time_ms": 312.5,
  "top_keywords": ["Federal Reserve", "interest rates", "inflation"],
  "timestamp": "2026-06-13T00:04:01"
}
```

---

## Technologies utilisees

| Categorie | Technologies |
|-----------|-------------|
| Big Data | Apache Spark 3.x, PySpark, Parquet |
| ML / NLP | HuggingFace Transformers, BERT, XLM-RoBERTa, PyTorch |
| Backend | FastAPI, SQLAlchemy, Uvicorn, Pydantic |
| Base de donnees | SQLite (dev), PostgreSQL 15 (production) |
| Frontend | React 18, Vite, Axios, Tailwind CSS |
| DevOps | Docker, Docker Compose, Nginx |
| Entrainement | Google Colab (GPU T4), HuggingFace Trainer |

---

Projet academique — Licence 3 Informatique, IA & Big Data.

github.com/d4ve07979/fake-news-detector
