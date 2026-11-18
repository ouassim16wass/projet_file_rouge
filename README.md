# GuardPay

Détection de fraude en temps réel sur les opérations d'une banque.
Projet fil rouge du titre RNCP Data Engineer (RNCP42655).

## Le cas d'usage

La Banque Aurore (fictive) propose la banque en ligne à ses clients : virements, retraits, versements et paiements.
Sa direction de la lutte contre la fraude doit repérer les opérations frauduleuses au moment où elles se produisent,
sans bloquer par erreur les clients honnêtes. La plateforme reçoit les opérations en continu, calcule un score de
risque explicable pour chacune et met les alertes à disposition des analystes par API et tableau de bord.

Le score est une aide à la décision : aucune opération n'est bloquée sans décision d'un analyste.

## Problématique

Comment détecter en temps réel les opérations frauduleuses d'une banque, avec un score explicable et un taux de
fausses alertes maîtrisé, sur une plateforme de données fiable, observable et déployable ?

## Objectifs

| # | Objectif | Indicateur | Bloc |
|---|---|---|---|
| O1 | Ingérer les opérations en continu sans perte ni doublon | 6 362 620 opérations rejouées, 0 doublon après reprise | BC02/03 |
| O2 | Préparer et fiabiliser les données | Rapport de qualité, quarantaine, catalogue complet | BC02 |
| O3 | Détecter la fraude avec un modèle évalué honnêtement | PaySim : au moins égal à la règle « montant égal au solde ». ULB : meilleur que la régression logistique | BC02/03 |
| O4 | Servir, orchestrer, déployer, surveiller | API sous 100 ms, Airflow, CI verte, monitoring actif | BC03 |
| O5 | Cadrer et piloter | Cahier des charges, planning, budget, KPI, formation | BC01/04 |

## Données

| Source | Contenu | Lien |
|---|---|---|
| PaySim (copie Hugging Face de la source Kaggle ealaxi/paysim1) | 6 362 620 opérations simulées, 8 213 fraudes (0,129 %), 743 pas de temps horaires | https://huggingface.co/datasets/theman10/paysim/resolve/main/paysim.csv |
| Fraude carte ULB | 284 807 transactions réelles anonymisées, 492 fraudes | https://openml.org/data/v1/download/1673544/creditcard.arff |

PaySim est synthétique et son signal est quasi trivial : la règle « le montant égale tout le solde du compte » détecte
97,5 % des fraudes (8 008 sur 8 213) sans aucune fausse alerte. PaySim valide donc la plateforme. Le jeu ULB, réel,
valide le modèle. Les comptes émetteurs ne reviennent presque jamais : les variables de fréquence portent sur le destinataire.

Télécharger les données :

```bash
python ingestion/telecharger_donnees.py
```

Les fichiers sont écrits dans `data/raw`, dossier exclu du dépôt.

## Stack

- Flux : Apache Kafka
- Traitement : PySpark Structured Streaming
- Stockage : Parquet (bronze, silver), PostgreSQL (gold), MongoDB (alertes, dossiers, rejets)
- Orchestration : Apache Airflow
- Modèle : scikit-learn, LightGBM, MLflow, SHAP
- API : FastAPI
- Déploiement : Docker Compose, GitHub Actions
- Monitoring : Prometheus, Grafana

## Architecture

```
PaySim  ->  rejeu Python  ->  Kafka  ->  PySpark Structured Streaming
                                              |
                       bronze (Parquet)  ->  silver  ->  gold (PostgreSQL)
                       MongoDB (alertes, dossiers, rejets)
                                              |
                                  modèle (MLflow)  ->  FastAPI  ->  Grafana
Airflow orchestre le réentraînement et les contrôles. Docker Compose lance la plateforme en local.
```

## Démarrage

```bash
cp .env.example .env
docker compose up -d
```

Rejouer les opérations vers Kafka puis lancer le job bronze :

```bash
pip install -r ingestion/requirements.txt
docker compose --profile streaming up -d spark-bronze
python ingestion/rejeu_kafka.py --pas-max 10 --secondes-par-pas 2
```

Services disponibles : Kafka sur le port 9092, PostgreSQL sur 5433, MongoDB sur 27017.
Modifier les mots de passe du fichier `.env` avant tout usage.

## Données : exploration, contrat, catalogue

```bash
pip install -r requirements-dev.txt
cp .env.example .env
make plateforme
make pipeline
make tests lint
```

Les contrats font référence : [`contrats/operations.yaml`](contrats/operations.yaml) (PaySim) et [`contrats/creditcard.yaml`](contrats/creditcard.yaml) (ULB), présentés dans [`docs/contrats_donnees.md`](docs/contrats_donnees.md). Le nettoyage écarte les lignes invalides vers la quarantaine, signale les anomalies tolérées et pseudonymise les comptes (variable `PSEUDO_SEL` du fichier `.env`). `make pipeline` enchaîne nettoyage, transformation, chargement PostgreSQL et catalogue. Rapports : `docs/rapport_exploration.md`, `docs/rapport_qualite.md`, `docs/rapport_qualite_cartes.md`, `docs/catalogue_donnees.md`. Déploiement, CI/CD et coûts : `docs/deploiement.md`, `docs/gestion_couts.md`, `docs/mesures_couts.md`.

## Structure du dépôt

```
docs/             cahier des charges, plan par phases, rapports, catalogue de données
contrats/         contrats de données
qualite/          application du contrat, nettoyage
exploration/      profilage des données
catalogue/        fiches des jeux de données
transformation/   variables du modèle et indicateurs (couche gold)
chargement/       chargement PostgreSQL
commun/           configuration partagée
.github/          intégration et livraison continues
outils/           scripts utilitaires (génération des documents)
ingestion/        téléchargement des données, rejeu vers Kafka
streaming/        jobs PySpark Structured Streaming
warehouse/        schémas PostgreSQL et MongoDB
orchestration/    DAGs Airflow
ml/               variables, entraînement, évaluation
api/              FastAPI
dashboards/       tableaux de bord Grafana
infra/            Dockerfiles et configuration des services
tests/
```

## Avancement

| Étape | Statut |
|---|---|
| Choix du sujet | fait |
| Cas d'usage, cahier des charges et catalogue (PDF) | fait |
| Arborescence, docker-compose (Kafka, PostgreSQL, MongoDB) | fait |
| Rejeu des opérations vers Kafka (`ingestion/rejeu_kafka.py`) | fait, testé sur 3 pas |
| Couche bronze Spark (`streaming/bronze.py`) | fait, testé : 4 274 lignes, 0 doublon |
| Phase 1 : exploration, contrats de données (PaySim, ULB), nettoyage, quarantaine, catalogue, 27 tests | fait (voir `docs/plan_phases.md`) |
| Phase 1 : transformations, gold, chargement PostgreSQL idempotent | fait, 2 770 409 lignes |
| Phase 1 : conteneur du pipeline, CI/CD, gestion des coûts | fait, workflows à valider sur GitHub |
| Silver en streaming avec le même contrat | à faire |
| Modèle de détection et suivi MLflow | à faire |
| API, Airflow, CI/CD, monitoring | à faire |
| Mémoire et soutenance | à faire |

## Régénérer le cahier des charges

```bash
pip install -r outils/generation_pdf/requirements.txt
python outils/generation_pdf/cahier_des_charges.py
```

Le PDF est écrit dans `docs/`. La commande se lance depuis la racine du dépôt.

## Livrables de la soutenance

- Dépôt GitHub documenté (code, Dockerfile, DAGs, tests, README d'architecture)
- Dossier de cadrage et d'architecture
- Démonstration : flux rejoué, API interrogée en direct, tableau de bord
- Mémoire et support de présentation
