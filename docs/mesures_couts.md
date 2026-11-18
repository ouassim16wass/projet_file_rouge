# Mesures de couts

Genere par `outils/mesurer_couts.py` sur la machine de developpement.

## Stockage fichiers

| Jeu | Taille (Mo) | Part du CSV PaySim |
|---|---|---|
| Brut PaySim (CSV) | 470.7 | 100% |
| Brut ULB (ARFF) | 143.8 | 31% |
| Silver operations (Parquet) | 375.4 | 80% |
| Silver cartes (Parquet) | 70.3 | 15% |
| Gold variables (Parquet zstd) | 112.4 | 24% |
| Gold indicateurs (Parquet zstd) | 0.1 | 0% |

## Stockage PostgreSQL (schema gold)

| Table | Total avec index (Mo) | Donnees seules (Mo) |
|---|---|---|
| variables_operation | 1 028.2 | 823.1 |
| indicateurs_horaires | 0.6 | 0.4 |
| journal_chargement | 0.0 | 0.0 |

## Duree de chargement

| Table | Duree max (s) |
|---|---|
| indicateurs_horaires | 0.04 |
| variables_operation | 29.67 |

## Ressources des conteneurs au repos

| Conteneur | Memoire utilisee / limite | CPU |
|---|---|---|
| guardpay-mongodb | 144.2MiB / 512MiB | 0.41% |
| guardpay-kafka | 301.7MiB / 768MiB | 2.30% |
| guardpay-postgres | 310.5MiB / 1GiB | 6.65% |
