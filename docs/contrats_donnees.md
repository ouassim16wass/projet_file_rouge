# Contrats de donnees GuardPay

Page generee par `catalogue/generer_contrats.py` a partir des fichiers `contrats/*.yaml`, qui font reference.
Chaque contrat fixe le schema, les regles de qualite, la fraicheur, la conservation et les conditions d'evolution entre le producteur et les consommateurs.

## guardpay.operations version 1.0.0

Fichier : [`contrats/operations.yaml`](../contrats/operations.yaml). Statut : actif. Jeu de donnees : D01-D02 operations.

Operations bancaires rejouees en continu depuis PaySim, telles que recues par la plateforme GuardPay.

### Engagements

| Element | Engagement |
|---|---|
| Proprietaire | equipe-donnees-guardpay |
| Consommateurs | streaming-silver, ml-entrainement, api-scoring, dashboards |
| Source | PaySim, Kaggle ealaxi/paysim1, donnees synthetiques, aucune donnee personnelle reelle |
| Licence | a verifier a la source d'origine |
| Livraison | continue, un pas de temps par intervalle de rejeu |
| Delai maximal d'ingestion | 60 secondes |
| Volume attendu | 6 362 620 lignes |
| Taux de rejet maximal | 0.10% |
| Conservation | 1 an |
| Evolution | ajout de champ optionnel autorise, suppression ou changement de type = nouvelle version majeure |
| Notification | revue du contrat avant tout changement de schema |

### Traitement des anomalies

- Erreur : ligne ecartee vers la quarantaine avec la liste des regles violees.
- Avertissement : ligne conservee, drapeau ajoute dans la colonne controles_qualite.

### Champs

| Champ | Source | Type | Obligatoire | Classification | Description | Regles |
|---|---|---|---|---|---|---|
| id_operation | genere | entier | oui | technique | Numero de ligne du fichier source, cle d'idempotence ajoutee a l'ingestion. | R01 (erreur) valeur au moins 1 |
| pas | step | entier | oui | technique | Pas de temps horaire, 1 correspond a la premiere heure. | R02 (erreur) entre 1 et 743 |
| type | type | texte | oui | metier | Nature de l'operation. | R03 (erreur) valeur parmi PAYMENT, TRANSFER, CASH_OUT, DEBIT, CASH_IN |
| montant | amount | decimal | oui | financier | Montant de l'operation. | R04 (erreur) valeur au moins 0; R05 (avertissement) montant nul, conserve car ces 16 operations sont des fraudes |
| emetteur | nameOrig | texte | oui | identifiant | Compte emetteur, pseudonymise par hachage sale en silver. | R06 (erreur) format `^C[0-9]+$`; pseudonymise |
| solde_emetteur_avant | oldbalanceOrg | decimal | oui | financier | Solde de l'emetteur avant l'operation. | R07 (erreur) valeur au moins 0 |
| solde_emetteur_apres | newbalanceOrig | decimal | oui | financier | Solde de l'emetteur apres l'operation. | R08 (erreur) valeur au moins 0 |
| destinataire | nameDest | texte | oui | identifiant | Compte destinataire (C client, M marchand), pseudonymise par hachage sale en silver. | R09 (erreur) format `^[CM][0-9]+$`; pseudonymise |
| solde_destinataire_avant | oldbalanceDest | decimal | oui | financier | Solde du destinataire avant l'operation, nul pour les marchands. | R10 (erreur) valeur au moins 0 |
| solde_destinataire_apres | newbalanceDest | decimal | oui | financier | Solde du destinataire apres l'operation, nul pour les marchands. | R11 (erreur) valeur au moins 0 |
| est_fraude | isFraud | entier | oui | cible | Etiquette de fraude, verite terrain. | R12 (erreur) valeur parmi 0, 1 |
| signalement_regle_existante | isFlaggedFraud | entier | oui | reference | Signalement par la regle metier existante du simulateur, 16 lignes sur 6 362 620. | R13 (erreur) valeur parmi 0, 1 |

### Regles portant sur la table

| ID | Nom | Severite | Description |
|---|---|---|---|
| R20 | unicite_id_operation | erreur | unicite_id_operation |
| R21 | unicite_cle_metier | erreur | unicite_cle_metier |
| R22 | pas_auto_virement | erreur | pas_auto_virement |
| R30 | solde_emetteur_non_suivi | avertissement | solde de l'emetteur a zero avant et apres, solde non suivi par la source |
| R31 | debit_plafonne | avertissement | montant superieur au solde, solde ramene a zero par la source |
| R32 | ecart_solde_emetteur | avertissement | ecart residuel entre solde avant, montant et solde apres |

## guardpay.transactions_cartes version 1.0.0

Fichier : [`contrats/creditcard.yaml`](../contrats/creditcard.yaml). Statut : actif. Jeu de donnees : D09 creditcard_ulb.

Transactions par carte reelles et anonymisees, utilisees pour valider le modele de detection.

### Engagements

| Element | Engagement |
|---|---|
| Proprietaire | equipe-donnees-guardpay |
| Consommateurs | ml-entrainement, ml-evaluation |
| Source | Fraude carte ULB, ULB Machine Learning Group, donnees reelles anonymisees, variables PCA |
| Licence | a verifier a la source d'origine |
| Livraison | statique, deux jours de septembre 2013 |
| Volume attendu | 284 807 lignes |
| Taux de rejet maximal | 1.00% |
| Conservation | duree du projet |
| Evolution | jeu statique, tout changement de schema = nouvelle version majeure |
| Notification | revue du contrat avant tout changement de schema |

### Traitement des anomalies

- Erreur : ligne ecartee vers la quarantaine avec la liste des regles violees.
- Avertissement : ligne conservee, drapeau ajoute dans la colonne controles_qualite.

### Champs

| Champ | Source | Type | Obligatoire | Classification | Description | Regles |
|---|---|---|---|---|---|---|
| id_transaction | genere | entier | oui | technique | Numero de ligne du fichier source, cle technique ajoutee a l'ingestion. | C01 (erreur) valeur au moins 1 |
| temps | Time | decimal | oui | technique | Delai ecoule depuis la premiere transaction du jeu, sur deux jours. | C02 (erreur) entre 0 et 172792 |
| v1 | V1 | decimal | oui | variable_pca | Composante principale 1 issue d'une analyse en composantes principales, anonymisee par la source. | - |
| v2 | V2 | decimal | oui | variable_pca | Composante principale 2 issue d'une analyse en composantes principales, anonymisee par la source. | - |
| v3 | V3 | decimal | oui | variable_pca | Composante principale 3 issue d'une analyse en composantes principales, anonymisee par la source. | - |
| v4 | V4 | decimal | oui | variable_pca | Composante principale 4 issue d'une analyse en composantes principales, anonymisee par la source. | - |
| v5 | V5 | decimal | oui | variable_pca | Composante principale 5 issue d'une analyse en composantes principales, anonymisee par la source. | - |
| v6 | V6 | decimal | oui | variable_pca | Composante principale 6 issue d'une analyse en composantes principales, anonymisee par la source. | - |
| v7 | V7 | decimal | oui | variable_pca | Composante principale 7 issue d'une analyse en composantes principales, anonymisee par la source. | - |
| v8 | V8 | decimal | oui | variable_pca | Composante principale 8 issue d'une analyse en composantes principales, anonymisee par la source. | - |
| v9 | V9 | decimal | oui | variable_pca | Composante principale 9 issue d'une analyse en composantes principales, anonymisee par la source. | - |
| v10 | V10 | decimal | oui | variable_pca | Composante principale 10 issue d'une analyse en composantes principales, anonymisee par la source. | - |
| v11 | V11 | decimal | oui | variable_pca | Composante principale 11 issue d'une analyse en composantes principales, anonymisee par la source. | - |
| v12 | V12 | decimal | oui | variable_pca | Composante principale 12 issue d'une analyse en composantes principales, anonymisee par la source. | - |
| v13 | V13 | decimal | oui | variable_pca | Composante principale 13 issue d'une analyse en composantes principales, anonymisee par la source. | - |
| v14 | V14 | decimal | oui | variable_pca | Composante principale 14 issue d'une analyse en composantes principales, anonymisee par la source. | - |
| v15 | V15 | decimal | oui | variable_pca | Composante principale 15 issue d'une analyse en composantes principales, anonymisee par la source. | - |
| v16 | V16 | decimal | oui | variable_pca | Composante principale 16 issue d'une analyse en composantes principales, anonymisee par la source. | - |
| v17 | V17 | decimal | oui | variable_pca | Composante principale 17 issue d'une analyse en composantes principales, anonymisee par la source. | - |
| v18 | V18 | decimal | oui | variable_pca | Composante principale 18 issue d'une analyse en composantes principales, anonymisee par la source. | - |
| v19 | V19 | decimal | oui | variable_pca | Composante principale 19 issue d'une analyse en composantes principales, anonymisee par la source. | - |
| v20 | V20 | decimal | oui | variable_pca | Composante principale 20 issue d'une analyse en composantes principales, anonymisee par la source. | - |
| v21 | V21 | decimal | oui | variable_pca | Composante principale 21 issue d'une analyse en composantes principales, anonymisee par la source. | - |
| v22 | V22 | decimal | oui | variable_pca | Composante principale 22 issue d'une analyse en composantes principales, anonymisee par la source. | - |
| v23 | V23 | decimal | oui | variable_pca | Composante principale 23 issue d'une analyse en composantes principales, anonymisee par la source. | - |
| v24 | V24 | decimal | oui | variable_pca | Composante principale 24 issue d'une analyse en composantes principales, anonymisee par la source. | - |
| v25 | V25 | decimal | oui | variable_pca | Composante principale 25 issue d'une analyse en composantes principales, anonymisee par la source. | - |
| v26 | V26 | decimal | oui | variable_pca | Composante principale 26 issue d'une analyse en composantes principales, anonymisee par la source. | - |
| v27 | V27 | decimal | oui | variable_pca | Composante principale 27 issue d'une analyse en composantes principales, anonymisee par la source. | - |
| v28 | V28 | decimal | oui | variable_pca | Composante principale 28 issue d'une analyse en composantes principales, anonymisee par la source. | - |
| montant | Amount | decimal | oui | financier | Montant de la transaction. | C03 (erreur) valeur au moins 0; C04 (avertissement) montant nul, conserve car 27 de ces transactions sont des fraudes |
| classe | Class | entier | oui | cible | Etiquette de fraude, verite terrain (1 fraude). | C05 (erreur) valeur parmi 0, 1 |

### Regles portant sur la table

| ID | Nom | Severite | Description |
|---|---|---|---|
| C20 | unicite_ligne_complete | erreur | transaction strictement identique a une autre, 1081 doublons dont 19 fraudes, ecartes pour eviter toute fuite entre apprentissage et test |
| C21 | unicite_id_transaction | erreur | unicite_id_transaction |
