# Rapport de qualite des donnees

Contrat `guardpay.transactions_cartes` version 1.0.0.

| Indicateur | Valeur |
|---|---|
| Lignes lues | 284 807 |
| Lignes en silver | 283 726 |
| Lignes en quarantaine | 1 081 |
| Taux de rejet | 0.3796% (seuil 1.00%) |
| Volume conforme au contrat | oui |
| Fraudes lues / conservees | 492 / 473 |
| Verdict | conforme |

| Regle | Severite | Description | Lignes | Dont fraudes |
|---|---|---|---|---|
| C04 | avertissement | montant nul, conserve car 27 de ces transactions sont des fraudes | 1 825 | 27 |
| C20 | erreur | transaction strictement identique a une autre, 1081 doublons dont 19 fraudes, ecartes pour eviter toute fuite entre apprentissage et test | 1 081 | 19 |
| C21 | erreur | unicite_id_transaction | 0 | 0 |
