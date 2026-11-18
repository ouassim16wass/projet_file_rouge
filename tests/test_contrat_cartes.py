import pandas as pd

from qualite.contrat import charger_contrat
from qualite.nettoyer import nettoyer

CONTRAT = charger_contrat("contrats/creditcard.yaml")


def transaction(**surcharge):
    base = {"temps": 10.0, "montant": 25.0, "classe": 0}
    base.update({f"v{i}": float(i) for i in range(1, 29)})
    base.update(surcharge)
    return base


def lancer(lignes):
    df = pd.DataFrame(lignes)
    df.insert(0, "id_transaction", range(1, len(df) + 1))
    return nettoyer(df, CONTRAT)


def test_transaction_valide():
    propre, quarantaine, *_ = lancer([transaction()])
    assert len(propre) == 1 and len(quarantaine) == 0


def test_doublon_exact_ecarte():
    propre, quarantaine, *_ = lancer([transaction(), transaction()])
    assert len(propre) == 1 and len(quarantaine) == 1
    assert "C20" in quarantaine.iloc[0]["regles_violees"]


def test_temps_hors_plage_et_classe_invalide():
    _, quarantaine, *_ = lancer([transaction(temps=999999.0), transaction(temps=11.0, classe=3)])
    assert len(quarantaine) == 2


def test_montant_nul_conserve_avec_avertissement():
    propre, *_ = lancer([transaction(montant=0.0)])
    assert "C04" in propre.iloc[0]["controles_qualite"]
