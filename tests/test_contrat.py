import pandas as pd
import pytest

from qualite.contrat import charger_contrat
from qualite.nettoyer import nettoyer

SEL = b"sel-de-test"


@pytest.fixture(scope="module")
def contrat():
    return charger_contrat()


def ligne(**surcharge):
    base = {
        "pas": 1,
        "type": "TRANSFER",
        "montant": 100.0,
        "emetteur": "C1",
        "solde_emetteur_avant": 500.0,
        "solde_emetteur_apres": 400.0,
        "destinataire": "C2",
        "solde_destinataire_avant": 0.0,
        "solde_destinataire_apres": 100.0,
        "est_fraude": 0,
        "signalement_regle_existante": 0,
    }
    base.update(surcharge)
    return base


def lancer(contrat, lignes):
    df = pd.DataFrame(lignes)
    df.insert(0, "id_operation", range(1, len(df) + 1))
    return nettoyer(df, contrat, SEL)


def test_ligne_valide_conservee(contrat):
    propre, quarantaine, *_ = lancer(contrat, [ligne()])
    assert len(propre) == 1 and len(quarantaine) == 0
    assert propre.iloc[0]["controles_qualite"] == ""


@pytest.mark.parametrize(
    "surcharge,regle",
    [
        ({"pas": 0}, "R02"),
        ({"pas": 744}, "R02"),
        ({"type": "VIREMENT"}, "R03"),
        ({"montant": -5.0}, "R04"),
        ({"emetteur": "X12"}, "R06"),
        ({"solde_emetteur_avant": -1.0}, "R07"),
        ({"destinataire": "Z9"}, "R09"),
        ({"est_fraude": 2}, "R12"),
        ({"destinataire": "C1"}, "R22"),
    ],
)
def test_ligne_invalide_mise_en_quarantaine(contrat, surcharge, regle):
    propre, quarantaine, *_ = lancer(contrat, [ligne(**surcharge)])
    assert len(propre) == 0 and len(quarantaine) == 1
    assert regle in quarantaine.iloc[0]["regles_violees"]


def test_valeur_manquante_rejetee(contrat):
    propre, quarantaine, *_ = lancer(contrat, [ligne(montant=None)])
    assert len(quarantaine) == 1
    assert "NUL_montant" in quarantaine.iloc[0]["regles_violees"]


def test_doublon_metier_rejete(contrat):
    propre, quarantaine, *_ = lancer(contrat, [ligne(), ligne()])
    assert len(propre) == 1 and len(quarantaine) == 1
    assert "R21" in quarantaine.iloc[0]["regles_violees"]


def test_montant_nul_conserve_avec_avertissement(contrat):
    propre, quarantaine, *_ = lancer(
        contrat, [ligne(montant=0.0, solde_emetteur_apres=500.0, est_fraude=1)]
    )
    assert len(propre) == 1 and len(quarantaine) == 0
    assert "R05" in propre.iloc[0]["controles_qualite"]


def test_solde_non_suivi_signale(contrat):
    propre, *_ = lancer(
        contrat, [ligne(solde_emetteur_avant=0.0, solde_emetteur_apres=0.0)]
    )
    assert "R30" in propre.iloc[0]["controles_qualite"]


def test_debit_plafonne_signale(contrat):
    propre, *_ = lancer(
        contrat, [ligne(montant=900.0, solde_emetteur_avant=500.0, solde_emetteur_apres=0.0)]
    )
    assert "R31" in propre.iloc[0]["controles_qualite"]


def test_pseudonymisation_stable_et_irreversible(contrat):
    propre, *_ = lancer(
        contrat,
        [ligne(), ligne(montant=200.0, destinataire="M7", solde_destinataire_apres=0.0)],
    )
    assert propre["emetteur"].nunique() == 1
    assert propre.iloc[0]["emetteur"] != "C1"
    assert len(propre.iloc[0]["emetteur"]) == 16
    assert list(propre["type_destinataire"]) == ["client", "marchand"]
