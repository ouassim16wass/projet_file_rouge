# Plan par phases

Chaque phase se termine par des livrables verifiables et se rattache aux blocs du titre RNCP Data Engineer.

| Phase | Contenu | Livrables | Bloc |
|---|---|---|---|
| 0 Cadrage | Sujet, problematique, objectifs, cahier des charges | PDF de cadrage, README | BC01, BC04 |
| 1 Donnees | Exploration, contrat de donnees, nettoyage, quarantaine, catalogue, tests | Rapport d'exploration, `contrats/operations.yaml`, rapport de qualite, catalogue, tests | BC01, BC02 |
| 2 Ingestion et streaming | Rejeu vers Kafka, bronze, silver en streaming avec le meme contrat, quarantaine Kafka et MongoDB | Jobs Spark, topics, reprise sans doublon | BC02, BC03 |
| 3 Entrepot | Schemas PostgreSQL gold, variables par operation, indicateurs horaires | SQL, tables gold, modele de donnees | BC01, BC02 |
| 4 Modele | References, regression logistique, LightGBM, cout metier, SHAP, suivi MLflow | Rapport d'evaluation, registre de modeles | BC02, BC03 |
| 5 Service | API FastAPI, alertes, dossiers dans MongoDB | API testee, documentation OpenAPI | BC03 |
| 6 Orchestration et deploiement | Airflow, Docker, integration continue, supervision | DAGs, pipeline CI, tableaux de bord | BC03 |
| 7 Pilotage et soutenance | KPI, budget, risques, memoire, support | Memoire, presentation, demonstration | BC04 |

Phase en cours : 1.

## Phase 1 en etapes

| Etape | Description | Statut |
|---|---|---|
| 1.1 | Explorer PaySim (`exploration/profil_paysim.py`) | fait |
| 1.2 | Contrat de donnees PaySim (`contrats/operations.yaml`) | fait |
| 1.3 | Nettoyer, mettre en quarantaine, pseudonymiser (`qualite/nettoyer.py`) | fait |
| 1.4 | Tester les contrats (`tests/`) | fait, 29 tests |
| 1.5 | Generer le catalogue (`catalogue/generer_catalogue.py`) | fait, PaySim et ULB |
| 1.6 | Explorer et contractualiser ULB (`contrats/creditcard.yaml`) | fait, 1 081 doublons ecartes |
| 1.7 | Transformer avant chargement (`transformation/variables.py`) : variables du modele, indicateurs horaires | fait |
| 1.8 | Charger dans PostgreSQL de facon idempotente (`chargement/charger_postgres.py`, `warehouse/sql`) | fait |
| 1.9 | Conteneuriser, CI/CD, gestion des couts (`infra/`, `.github/workflows`, `docs/deploiement.md`, `docs/gestion_couts.md`) | fait |
| 1.10 | Catalogue de donnees en page HTML interactive (`docs/catalogue.html`) | fait |
| 1.11 | CI decoupee en 8 jobs, CD en 5 jobs, controle des donnees a la demande | fait |
| 1.12 | Mettre a jour le PDF de cadrage avec les constats | a faire |
