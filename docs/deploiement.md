# Deploiement, CI et CD

## Environnements

| Environnement | Moyen | Usage |
|---|---|---|
| Developpement | `make plateforme` puis `make pipeline` | Travail quotidien sur la machine locale |
| Integration | GitHub Actions, `.github/workflows/ci.yml` | Verification de chaque push et de chaque pull request |
| Livraison | GitHub Actions, `.github/workflows/cd.yml`, sur tag `v*` | Image publiee dans le registre GitHub, version de livraison creee |

## Integration continue

Le workflow `ci.yml` est decoupe en jobs independants, lances en parallele, puis enchaines par dependances :

| Job | Controle | Depend de |
|---|---|---|
| 1 Lint | `ruff check` | aucun |
| 2 Tests unitaires | `pytest` (29 tests : contrats, nettoyage, transformations) | aucun |
| 3 Contrats de donnees | `qualite/verifier_contrats.py` : structure, identifiants uniques, severites, champs references | aucun |
| 4 Audit des dependances | `pip-audit` sur les dependances d'execution | aucun |
| 5 Schema PostgreSQL | Scripts `warehouse/sql` appliques sur un PostgreSQL de test, erreur bloquante | aucun |
| 6 Configuration Docker Compose | Validation du compose avec tous les profils | aucun |
| 7 Image du pipeline | Construction, import des bibliotheques, controle des contrats dans l'image | 1, 2, 3, 6 |
| 8 Bilan | Echoue si un job a echoue ou ete annule | tous |

Les executions concurrentes d'une meme branche sont annulees pour limiter les minutes consommees.

## Controle des donnees

Le workflow `donnees.yml`, lance a la demande, enchaine deux jobs : controle des contrats, puis telechargement du jeu ULB, nettoyage selon le contrat et publication du rapport de qualite comme artefact.

## Livraison continue

Le workflow `cd.yml` se declenche en poussant un tag : `git tag v0.1.0 && git push origin v0.1.0`. Il enchaine cinq jobs :

| Job | Action | Depend de |
|---|---|---|
| 1 Controles d'integration | Rejoue tout `ci.yml` | aucun |
| 2 Construction de l'image | Construit l'image et la transmet au job suivant | 1 |
| 3 Publication | Pousse `ghcr.io/<proprietaire>/guardpay-pipeline:<tag>` et `latest` | 2 |
| 4 Verification de l'image publiee | Tire l'image depuis le registre et controle les contrats | 3 |
| 5 Version de livraison | Cree la release avec ses notes | 4 |

Retour arriere : relancer la plateforme avec le tag precedent de l'image.

## Deploiement de la plateforme

```bash
cp .env.example .env
docker compose up -d kafka kafka-init postgres mongodb
docker compose --profile batch run --rm pipeline qualite/nettoyer.py
docker compose --profile batch run --rm pipeline transformation/variables.py
docker compose --profile batch run --rm pipeline chargement/charger_postgres.py
```

Les secrets (mots de passe, sel de pseudonymisation) sont lus dans `.env`, jamais dans l'image ni dans le depot. Le conteneur du pipeline s'execute sans droits administrateur.

## Prochaines etapes

Orchestration par Airflow (phase 6), supervision Prometheus et Grafana, deploiement des services applicatifs (API) avec leur propre image.
