PYTHON ?= python3

.PHONY: installer donnees nettoyer transformer charger catalogue tests lint plateforme arreter pipeline image

installer:
	$(PYTHON) -m pip install -r requirements-dev.txt

donnees:
	$(PYTHON) ingestion/telecharger_donnees.py

nettoyer:
	$(PYTHON) qualite/nettoyer.py

transformer:
	$(PYTHON) transformation/variables.py

charger:
	$(PYTHON) chargement/charger_postgres.py

catalogue:
	$(PYTHON) catalogue/generer_catalogue.py

pipeline: nettoyer transformer charger catalogue

tests:
	$(PYTHON) -m pytest

lint:
	ruff check .

plateforme:
	docker compose up -d kafka kafka-init postgres mongodb

arreter:
	docker compose down

image:
	docker build -f infra/Dockerfile.pipeline -t guardpay-pipeline:local .
