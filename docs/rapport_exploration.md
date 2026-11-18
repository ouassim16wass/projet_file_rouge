# Rapport d'exploration de PaySim

Mesures faites par `exploration/profil_paysim.py` sur le fichier complet : 6 362 620 lignes, 11 colonnes, 743 pas de temps.

## Ce qui est propre

| Controle | Resultat |
|---|---|
| Valeurs manquantes | 0 |
| Doublons exacts et doublons sur (pas, emetteur, destinataire, montant) | 0 |
| Formats de comptes (emetteur C..., destinataire C... ou M...) | 0 invalide |
| Soldes negatifs | 0 |
| Auto-virements | 0 |
| Pas de temps manquants | 0 |

## Ce qui demande une decision

| Constat | Mesure | Decision |
|---|---|---|
| Montants a 0 | 16 operations CASH_OUT, toutes frauduleuses | Conservees avec un avertissement (R05). Les rejeter ferait perdre 16 fraudes. |
| Solde emetteur a 0 avant et apres, hors CASH_IN | 2 088 985 operations | Solde non suivi par la source. Avertissement R30, ligne conservee. |
| Montant superieur au solde, solde ramene a 0 | 1 512 573 operations | Debit plafonne par le simulateur. Avertissement R31, ligne conservee. |
| Autre ecart entre solde, montant et solde apres | 76 866 operations | Avertissement R32, ligne conservee. |
| Colonne isFlaggedFraud | 16 lignes, toutes frauduleuses | Gardee comme reference de comparaison, interdite comme variable. |
| Destinataires marchands (M) | 2 151 495 operations, soldes toujours nuls | Normal : la source ne suit pas les soldes des marchands. Colonne `type_destinataire` ajoutee. |

Les incoherences de solde touchent 74 % des debits hors CASH_IN (3 678 407 sur 4 963 336) : les rejeter detruirait le jeu. Le contrat les signale sans les ecarter.

## Ce qui concerne la fraude

| Constat | Mesure |
|---|---|
| Fraudes | 8 213 sur 6 362 620, soit 0,129 % |
| Types touches | TRANSFER (4 097) et CASH_OUT (4 116) uniquement |
| Types sans aucune fraude | PAYMENT, CASH_IN, DEBIT |
| Fraudes avec solde emetteur a 0 avant | 41 seulement |
| Comptes emetteurs distincts | 6 353 307 pour 6 362 620 operations : pas d'historique par client |
| Operations par pas de temps | de 2 a 51 352 |

Consequence pour le modele : il porte sur TRANSFER et CASH_OUT (2 770 409 operations) et ses variables viennent de l'operation et du destinataire, pas de l'historique de l'emetteur.
