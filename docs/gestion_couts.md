# Gestion des couts

La plateforme tourne en local, sans compte cloud. Les couts sont donc mesures en ressources (stockage, memoire, calcul, temps) et traduits en leviers applicables a un deploiement cloud. Les mesures sont dans `docs/mesures_couts.md`, regenerees par `outils/mesurer_couts.py`.

## Leviers appliques

| Levier | Mise en oeuvre | Effet mesure |
|---|---|---|
| Format colonne compresse | Parquet, zstd pour la couche gold | Gold variables : 112 Mo, soit 24 % du CSV PaySim (471 Mo) |
| Retention Kafka bornee | `KAFKA_LOG_RETENTION_HOURS=24` et `KAFKA_LOG_RETENTION_BYTES=2 Go` | Le disque du broker ne croit pas avec le rejeu |
| Plafonds de ressources | `mem_limit` et `cpus` sur chaque service du compose | Kafka 768 Mo, PostgreSQL 1 Go, MongoDB 512 Mo, Spark 2 Go, pipeline 6 Go |
| Tas JVM borne | `KAFKA_HEAP_OPTS=-Xms384m -Xmx384m` | Kafka au repos : environ 300 Mo |
| Services a la demande | Profils `streaming` et `batch` : Spark et le pipeline ne tournent que sur demande | Aucun calcul inutile au repos |
| Chargement incremental idempotent | Upsert par cle dans PostgreSQL | Une reprise ne duplique rien et ne force pas de rechargement complet |
| Perimetre reduit | Perimetre du modele limite a TRANSFER et CASH_OUT | 2 770 409 lignes en gold au lieu de 6 362 620 |
| Retentions par jeu | Colonne `retention` du catalogue (90 jours a 5 ans) | Base de la purge, a automatiser avec Airflow |
| Cache de CI | Cache pip, annulation des executions superseded | Moins de minutes d'execution |

## Constat a traiter

La table `gold.variables_operation` pese 1 028 Mo dans PostgreSQL (dont 205 Mo d'index) pour 112 Mo en Parquet zstd, soit environ neuf fois plus. Pistes, a trancher en phase 3 :

1. Garder le detail en Parquet pour l'entrainement et ne charger dans PostgreSQL que les colonnes servies par l'API et les tableaux de bord.
2. Partitionner par `pas` et purger les partitions anciennes selon la retention.
3. Retirer les index non utilises par les requetes reelles.

## Estimation cloud

Elle sera faite avec les quantites mesurees, multipliees par la grille tarifaire du fournisseur retenu au moment du chiffrage, sans prix recopies de memoire :

| Poste | Quantite mesuree | Source |
|---|---|---|
| Stockage objet (bronze, silver, gold) | environ 560 Mo pour PaySim, tailles dans `docs/mesures_couts.md` | `outils/mesurer_couts.py` |
| Base relationnelle | 1 a 2 Go de donnees gold | `pg_total_relation_size` |
| Calcul batch | environ 30 s de nettoyage, 30 s de chargement par execution complete | journal `gold.journal_chargement` |
| Streaming | 1 broker, 1 job Spark, debit moyen 1 700 evenements par seconde et pic 10 300 | cahier des charges |
| Image applicative | 867 Mo | `docker image ls` |

Un cout mensuel sera calcule dans le memoire par scenario : developpement (arrets hors usage), production (fonctionnement continu), avec les memes quantites.

## Suivi

Le DAG Airflow `catalog_refresh` (phase 6) republiera volumes, fraicheur et taux de rejet. Les alertes de budget et les tableaux de bord de ressources seront ajoutes avec Prometheus et Grafana.
