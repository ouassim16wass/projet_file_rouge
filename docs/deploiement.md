# Deploiement, CI et CD

## Environnements

| Environnement | Moyen | Usage |
|---|---|---|
| Developpement | `make plateforme` puis `make pipeline` | Travail quotidien sur la machine locale |
| Integration | GitHub Actions, `.github/workflows/ci.yml` | Verification de chaque push et de chaque pull request |
| Livraison | GitHub Actions, `.github/workflows/cd.yml`, sur tag `v*` | Image publiee dans le registre GitHub, version de livraison creee |

## Integration continue

| Job | Controle |
|---|---|
| `qualite-code` | Lint `ruff`, tests `pytest` (27 tests : contrats, nettoyage, transformations) |
| `audit-dependances` | `pip-audit` sur les dependances d'execution |
| `schema-sql` | Application des scripts `warehouse/sql` sur un PostgreSQL de test, erreur bloquante |
| `compose-et-image` | Validation du `docker-compose.yml` avec tous les profils, construction de l'image du pipeline, import des bibliotheques dans l'image |

Les executions concurrentes d'une meme branche sont annulees pour limiter les minutes consommees.

## Livraison continue

Une release se declenche en poussant un tag : `git tag v0.1.0 && git push origin v0.1.0`. Le workflow rejoue lint et tests, construit `infra/Dockerfile.pipeline`, publie `ghcr.io/<proprietaire>/guardpay-pipeline:<tag>` et `latest`, puis cree la release avec ses notes.

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
