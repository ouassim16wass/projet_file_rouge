import pandas as pd

from transformation.variables import calculer_indicateurs, calculer_variables


def silver(lignes):
    base = {
        "type": "TRANSFER",
        "montant": 100.0,
        "destinataire": "d1",
        "emetteur": "e1",
        "solde_emetteur_avant": 100.0,
        "solde_emetteur_apres": 0.0,
        "solde_destinataire_avant": 0.0,
        "solde_destinataire_apres": 100.0,
        "type_destinataire": "client",
        "est_fraude": 0,
        "controles_qualite": "",
        "pas": 1,
    }
    df = pd.DataFrame([{**base, **ligne} for ligne in lignes])
    df.insert(0, "id_operation", range(1, len(df) + 1))
    return df


def test_perimetre_limite_aux_transferts_et_retraits():
    df = silver([{"type": "PAYMENT"}, {"type": "CASH_IN"}, {"type": "TRANSFER"}, {"type": "CASH_OUT"}])
    assert set(calculer_variables(df)["type"]) == {"TRANSFER", "CASH_OUT"}


def test_montant_egal_solde_et_compte_vide():
    v = calculer_variables(silver([{}, {"montant": 40.0, "solde_emetteur_apres": 60.0}]))
    assert list(v["montant_egal_solde"]) == [True, False]
    assert list(v["compte_vide_apres"]) == [True, False]


def test_historique_destinataire_ne_regarde_que_le_passe():
    v = calculer_variables(silver([{}, {"montant": 50.0}, {"montant": 10.0}]))
    assert list(v["nb_recus_destinataire_avant"]) == [0, 1, 2]
    assert list(v["montant_recu_destinataire_avant"]) == [0.0, 100.0, 150.0]
    assert list(v["destinataire_inconnu"]) == [True, False, False]


def test_decoupage_temporel():
    v = calculer_variables(silver([{"pas": 323}, {"pas": 324}]))
    assert list(v["jeu_donnees"]) == ["apprentissage", "test"]


def test_heure_du_jour_et_jour():
    v = calculer_variables(silver([{"pas": 1}, {"pas": 25}, {"pas": 26}]))
    assert list(v["heure_du_jour"]) == [0, 0, 1]
    assert list(v["jour"]) == [0, 1, 1]


def test_part_solde_absente_si_solde_nul():
    v = calculer_variables(silver([{"solde_emetteur_avant": 0.0, "solde_emetteur_apres": 0.0}]))
    assert pd.isna(v.loc[0, "part_solde_deplacee"])


def test_indicateurs_horaires():
    df = silver([{"est_fraude": 1, "controles_qualite": "R30"}, {}, {"type": "PAYMENT"}])
    i = calculer_indicateurs(df).set_index("type")
    assert i.loc["TRANSFER", "nb_operations"] == 2
    assert i.loc["TRANSFER", "nb_fraudes"] == 1
    assert i.loc["TRANSFER", "nb_avertissements"] == 1
    assert i.loc["PAYMENT", "nb_operations"] == 1
