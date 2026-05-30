# Makefile — Commandes raccourcies pour le projet
# Usage: make <commande>

.PHONY: help install dev build test clean

help:
	@echo "Commandes disponibles :"
	@echo "  make install     — Installe toutes les dépendances"
	@echo "  make dev         — Lance en mode développement (sans Docker)"
	@echo "  make build       — Construit et lance avec Docker Compose"
	@echo "  make test        — Lance les tests unitaires"
	@echo "  make clean       — Supprime les containers Docker"
	@echo "  make logs        — Affiche les logs Docker"
	@echo "  make eda         — Lance l'analyse exploratoire"

install:
	cd backend && pip install -r requirements.txt
	cd frontend && npm install
	cd ml && pip install -r requirements_ml.txt

dev:
	@echo "Lancement du backend..."
	cd backend && uvicorn app.main:app --reload --port 8000 &
	@echo "Lancement du frontend..."
	cd frontend && npm run dev

build:
	docker-compose up --build

stop:
	docker-compose down

test:
	cd backend && pytest tests/ -v --tb=short

logs:
	docker-compose logs -f

eda:
	cd ml/notebooks && python eda_analysis.py

clean:
	docker-compose down -v
	docker system prune -f
