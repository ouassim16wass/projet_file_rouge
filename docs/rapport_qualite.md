# Rapport de qualite des donnees

Contrat `guardpay.operations` version 1.0.0.

| Indicateur | Valeur |
|---|---|
| Lignes lues | 6 362 620 |
| Lignes en silver | 6 362 620 |
| Lignes en quarantaine | 0 |
| Taux de rejet | 0.0000% (seuil 0.10%) |
| Volume conforme au contrat | oui |
| Fraudes lues / conservees | 8 213 / 8 213 |
| Verdict | conforme |

| Regle | Severite | Description | Lignes | Dont fraudes |
|---|---|---|---|---|
| R05 | avertissement | montant nul, conserve car ces 16 operations sont des fraudes | 16 | 16 |
| R20 | erreur | unicite_id_operation | 0 | 0 |
| R21 | erreur | unicite_cle_metier | 0 | 0 |
| R22 | erreur | pas_auto_virement | 0 | 0 |
| R30 | avertissement | solde de l'emetteur a zero avant et apres, solde non suivi par la source | 2 088 985 | 41 |
| R31 | avertissement | montant superieur au solde, solde ramene a zero par la source | 1 512 573 | 4 |
| R32 | avertissement | ecart residuel entre solde avant, montant et solde apres | 76 866 | 16 |
