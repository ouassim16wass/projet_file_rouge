# Catalogue de donnees GuardPay

Genere par `catalogue/generer_catalogue.py` a partir des contrats `contrats/*.yaml`, de `catalogue/jeux_de_donnees.yaml` et des statistiques mesurees sur le silver.

## Sources

| ID | Nom | Nature | Origine | Licence | URL |
|---|---|---|---|---|---|
| S1 | PaySim | synthetique | Kaggle ealaxi/paysim1 | a verifier a la source d'origine | https://huggingface.co/datasets/theman10/paysim/resolve/main/paysim.csv |
| S2 | Fraude carte ULB | reelle anonymisee | ULB Machine Learning Group | a verifier a la source d'origine | https://openml.org/data/v1/download/1673544/creditcard.arff |

## Jeux de donnees

| ID | Nom | Couche | Stockage | Source | Cle | Frequence | Sensibilite | Retention | Statut |
|---|---|---|---|---|---|---|---|---|---|
| D01 | operations_brutes | bronze | Kafka operations.brutes + Parquet data/processed/bronze | PaySim (S1) | id_operation | continue | moyenne | 1 an | realise |
| D02 | operations_propres | silver | Parquet data/processed/silver/operations.parquet | D01 | id_operation | continue | moyenne | 1 an | realise |
| D03 | variables_operation | gold | Parquet data/processed/gold + PostgreSQL gold.variables_operation | D02 | id_operation | continue | moyenne | par version du modele | realise en lot |
| D04 | scores_operations | gold | PostgreSQL | D03, modele | id_operation | continue | moyenne | 2 ans | prevu |
| D05 | alertes | gold | MongoDB | D04 | id_alerte | continue | moyenne | 2 ans | prevu |
| D06 | dossiers_investigation | gold | MongoDB | D05 | id_dossier | a la decision | moyenne | 5 ans | prevu |
| D07 | operations_rejetees | quarantaine | Kafka operations.rejetees + Parquet data/processed/quarantaine | D01 | id_operation | continue | faible | 90 jours | realise |
| D08 | indicateurs_horaires | gold | Parquet data/processed/gold + PostgreSQL gold.indicateurs_horaires | D02 | pas + type | horaire | faible | duree du service | realise en lot |
| D09 | creditcard_ulb | silver | Parquet data/processed/silver/transactions_cartes.parquet | ULB (S2) | id_transaction | statique | faible | duree du projet | realise |
| D10 | modeles | registre | MLflow | entrainement | version | a chaque entrainement | faible | toutes versions | prevu |

## Dictionnaire D02 operations_propres

6 362 620 lignes. Contrat `guardpay.operations` version 1.0.0.

| Champ | Type | Classification | Description | Regles | Min | Max | Distincts | Nuls |
|---|---|---|---|---|---|---|---|---|
| id_operation | entier | technique | Numero de ligne du fichier source, cle d'idempotence ajoutee a l'ingestion. | R01 unique | 1.00 | 6 362 620.00 | 6362620 | 0 |
| pas | entier | technique | Pas de temps horaire, 1 correspond a la premiere heure. | R02 | 1.00 | 743.00 | 743 | 0 |
| type | texte | metier | Nature de l'operation. | R03 | - | - | 5 | 0 |
| montant | decimal | financier | Montant de l'operation. | R04, R05 | 0.00 | 92 445 516.64 | 5316900 | 0 |
| emetteur | texte | identifiant | Compte emetteur, pseudonymise par hachage sale en silver. | R06 | - | - | 6353307 | 0 |
| solde_emetteur_avant | decimal | financier | Solde de l'emetteur avant l'operation. | R07 | 0.00 | 59 585 040.37 | 1845844 | 0 |
| solde_emetteur_apres | decimal | financier | Solde de l'emetteur apres l'operation. | R08 | 0.00 | 49 585 040.37 | 2682586 | 0 |
| destinataire | texte | identifiant | Compte destinataire (C client, M marchand), pseudonymise par hachage sale en silver. | R09 | - | - | 2722362 | 0 |
| solde_destinataire_avant | decimal | financier | Solde du destinataire avant l'operation, nul pour les marchands. | R10 | 0.00 | 356 015 889.35 | 3614697 | 0 |
| solde_destinataire_apres | decimal | financier | Solde du destinataire apres l'operation, nul pour les marchands. | R11 | 0.00 | 356 179 278.92 | 3555499 | 0 |
| est_fraude | entier | cible | Etiquette de fraude, verite terrain. | R12 | 0.00 | 1.00 | 2 | 0 |
| signalement_regle_existante | entier | reference | Signalement par la regle metier existante du simulateur, 16 lignes sur 6 362 620. | R13 | 0.00 | 1.00 | 2 | 0 |
| type_destinataire | texte | derive | client ou marchand, deduit du prefixe du compte destinataire. | - | - | - | 2 | 0 |
| controles_qualite | texte | technique | Identifiants des regles d'avertissement declenchees, separes par des virgules. | - | - | - | 5 | 0 |

## Regles de qualite : guardpay.operations

| ID | Portee | Severite | Description |
|---|---|---|---|
| R01 | id_operation | erreur | minimum |
| R02 | pas | erreur | plage |
| R03 | type | erreur | valeurs |
| R04 | montant | erreur | minimum |
| R05 | montant | avertissement | montant nul, conserve car ces 16 operations sont des fraudes |
| R06 | emetteur | erreur | format |
| R07 | solde_emetteur_avant | erreur | minimum |
| R08 | solde_emetteur_apres | erreur | minimum |
| R09 | destinataire | erreur | format |
| R10 | solde_destinataire_avant | erreur | minimum |
| R11 | solde_destinataire_apres | erreur | minimum |
| R12 | est_fraude | erreur | valeurs |
| R13 | signalement_regle_existante | erreur | valeurs |
| R20 | table | erreur | unicite_id_operation |
| R21 | table | erreur | unicite_cle_metier |
| R22 | table | erreur | pas_auto_virement |
| R30 | table | avertissement | solde de l'emetteur a zero avant et apres, solde non suivi par la source |
| R31 | table | avertissement | montant superieur au solde, solde ramene a zero par la source |
| R32 | table | avertissement | ecart residuel entre solde avant, montant et solde apres |

Derniere mesure : 6 362 620 lignes lues, 0 en quarantaine, verdict conforme. Detail dans `docs/rapport_qualite.md`.

## Dictionnaire D09 creditcard_ulb

283 726 lignes. Contrat `guardpay.transactions_cartes` version 1.0.0.

| Champ | Type | Classification | Description | Regles | Min | Max | Distincts | Nuls |
|---|---|---|---|---|---|---|---|---|
| id_transaction | entier | technique | Numero de ligne du fichier source, cle technique ajoutee a l'ingestion. | C01 unique | 1.00 | 284 807.00 | 283726 | 0 |
| temps | decimal | technique | Delai ecoule depuis la premiere transaction du jeu, sur deux jours. | C02 | 0.00 | 172 792.00 | 124592 | 0 |
| v1 | decimal | variable_pca | Composante principale 1 issue d'une analyse en composantes principales, anonymisee par la source. | - | -56.41 | 2.45 | 275663 | 0 |
| v2 | decimal | variable_pca | Composante principale 2 issue d'une analyse en composantes principales, anonymisee par la source. | - | -72.72 | 22.06 | 275663 | 0 |
| v3 | decimal | variable_pca | Composante principale 3 issue d'une analyse en composantes principales, anonymisee par la source. | - | -48.33 | 9.38 | 275663 | 0 |
| v4 | decimal | variable_pca | Composante principale 4 issue d'une analyse en composantes principales, anonymisee par la source. | - | -5.68 | 16.88 | 275663 | 0 |
| v5 | decimal | variable_pca | Composante principale 5 issue d'une analyse en composantes principales, anonymisee par la source. | - | -113.74 | 34.80 | 275663 | 0 |
| v6 | decimal | variable_pca | Composante principale 6 issue d'une analyse en composantes principales, anonymisee par la source. | - | -26.16 | 73.30 | 275663 | 0 |
| v7 | decimal | variable_pca | Composante principale 7 issue d'une analyse en composantes principales, anonymisee par la source. | - | -43.56 | 120.59 | 275663 | 0 |
| v8 | decimal | variable_pca | Composante principale 8 issue d'une analyse en composantes principales, anonymisee par la source. | - | -73.22 | 20.01 | 275663 | 0 |
| v9 | decimal | variable_pca | Composante principale 9 issue d'une analyse en composantes principales, anonymisee par la source. | - | -13.43 | 15.59 | 275663 | 0 |
| v10 | decimal | variable_pca | Composante principale 10 issue d'une analyse en composantes principales, anonymisee par la source. | - | -24.59 | 23.75 | 275663 | 0 |
| v11 | decimal | variable_pca | Composante principale 11 issue d'une analyse en composantes principales, anonymisee par la source. | - | -4.80 | 12.02 | 275663 | 0 |
| v12 | decimal | variable_pca | Composante principale 12 issue d'une analyse en composantes principales, anonymisee par la source. | - | -18.68 | 7.85 | 275663 | 0 |
| v13 | decimal | variable_pca | Composante principale 13 issue d'une analyse en composantes principales, anonymisee par la source. | - | -5.79 | 7.13 | 275663 | 0 |
| v14 | decimal | variable_pca | Composante principale 14 issue d'une analyse en composantes principales, anonymisee par la source. | - | -19.21 | 10.53 | 275663 | 0 |
| v15 | decimal | variable_pca | Composante principale 15 issue d'une analyse en composantes principales, anonymisee par la source. | - | -4.50 | 8.88 | 275663 | 0 |
| v16 | decimal | variable_pca | Composante principale 16 issue d'une analyse en composantes principales, anonymisee par la source. | - | -14.13 | 17.32 | 275663 | 0 |
| v17 | decimal | variable_pca | Composante principale 17 issue d'une analyse en composantes principales, anonymisee par la source. | - | -25.16 | 9.25 | 275663 | 0 |
| v18 | decimal | variable_pca | Composante principale 18 issue d'une analyse en composantes principales, anonymisee par la source. | - | -9.50 | 5.04 | 275663 | 0 |
| v19 | decimal | variable_pca | Composante principale 19 issue d'une analyse en composantes principales, anonymisee par la source. | - | -7.21 | 5.59 | 275663 | 0 |
| v20 | decimal | variable_pca | Composante principale 20 issue d'une analyse en composantes principales, anonymisee par la source. | - | -54.50 | 39.42 | 275663 | 0 |
| v21 | decimal | variable_pca | Composante principale 21 issue d'une analyse en composantes principales, anonymisee par la source. | - | -34.83 | 27.20 | 275663 | 0 |
| v22 | decimal | variable_pca | Composante principale 22 issue d'une analyse en composantes principales, anonymisee par la source. | - | -10.93 | 10.50 | 275663 | 0 |
| v23 | decimal | variable_pca | Composante principale 23 issue d'une analyse en composantes principales, anonymisee par la source. | - | -44.81 | 22.53 | 275663 | 0 |
| v24 | decimal | variable_pca | Composante principale 24 issue d'une analyse en composantes principales, anonymisee par la source. | - | -2.84 | 4.58 | 275663 | 0 |
| v25 | decimal | variable_pca | Composante principale 25 issue d'une analyse en composantes principales, anonymisee par la source. | - | -10.30 | 7.52 | 275663 | 0 |
| v26 | decimal | variable_pca | Composante principale 26 issue d'une analyse en composantes principales, anonymisee par la source. | - | -2.60 | 3.52 | 275663 | 0 |
| v27 | decimal | variable_pca | Composante principale 27 issue d'une analyse en composantes principales, anonymisee par la source. | - | -22.57 | 31.61 | 275663 | 0 |
| v28 | decimal | variable_pca | Composante principale 28 issue d'une analyse en composantes principales, anonymisee par la source. | - | -15.43 | 33.85 | 275663 | 0 |
| montant | decimal | financier | Montant de la transaction. | C03, C04 | 0.00 | 25 691.16 | 32767 | 0 |
| classe | entier | cible | Etiquette de fraude, verite terrain (1 fraude). | C05 | 0.00 | 1.00 | 2 | 0 |
| controles_qualite | texte | technique | Identifiants des regles d'avertissement declenchees, separes par des virgules. | - | - | - | 2 | 0 |

## Regles de qualite : guardpay.transactions_cartes

| ID | Portee | Severite | Description |
|---|---|---|---|
| C01 | id_transaction | erreur | minimum |
| C02 | temps | erreur | plage |
| C03 | montant | erreur | minimum |
| C04 | montant | avertissement | montant nul, conserve car 27 de ces transactions sont des fraudes |
| C05 | classe | erreur | valeurs |
| C20 | table | erreur | transaction strictement identique a une autre, 1081 doublons dont 19 fraudes, ecartes pour eviter toute fuite entre apprentissage et test |
| C21 | table | erreur | unicite_id_transaction |

Derniere mesure : 284 807 lignes lues, 1081 en quarantaine, verdict conforme. Detail dans `docs/rapport_qualite_cartes.md`.
