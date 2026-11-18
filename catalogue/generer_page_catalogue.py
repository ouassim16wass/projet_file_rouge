import json
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from qualite.contrat import charger_contrat

MODELE = Path("catalogue/modele_page_catalogue.html")
SORTIE = Path("docs/catalogue.html")
JEUX = Path("catalogue/jeux_de_donnees.yaml")
CATALOGUE = Path("catalogue/catalogue.json")
DEPOT = "https://github.com/ouassim16wass/projet_file_rouge"

BASE_PAYSIM = {
    "pas": 1,
    "type": "TRANSFER",
    "montant": 181,
    "emetteur": "C1305486145",
    "solde_emetteur_avant": 181,
    "solde_emetteur_apres": 0,
    "destinataire": "C553264065",
    "solde_destinataire_avant": 0,
    "solde_destinataire_apres": 0,
    "est_fraude": 1,
    "signalement_regle_existante": 0,
}

CAS_PAYSIM = [
    {"nom": "Paiement normal", "valeurs": {"type": "PAYMENT", "montant": 1864.28, "solde_emetteur_avant": 21249, "solde_emetteur_apres": 19384.72, "destinataire": "M2044282225", "est_fraude": 0}},
    {"nom": "Montant nul", "valeurs": {"type": "CASH_OUT", "montant": 0, "solde_emetteur_avant": 0, "solde_emetteur_apres": 0}},
    {"nom": "Solde non suivi", "valeurs": {"type": "PAYMENT", "montant": 100, "solde_emetteur_avant": 0, "solde_emetteur_apres": 0, "destinataire": "M1", "est_fraude": 0}},
    {"nom": "Débit plafonné", "valeurs": {"type": "CASH_OUT", "montant": 900, "solde_emetteur_avant": 500, "solde_emetteur_apres": 0}},
    {"nom": "Pas hors plage", "valeurs": {"pas": 800}},
    {"nom": "Type inconnu", "valeurs": {"type": "VIREMENT"}},
    {"nom": "Montant négatif", "valeurs": {"montant": -5}},
    {"nom": "Compte mal formé", "valeurs": {"emetteur": "X12"}},
    {"nom": "Auto-virement", "valeurs": {"destinataire": "C1305486145"}},
]

BASE_CARTES = {"temps": 406, "montant": 149.62, "classe": 0, **{f"v{i}": 0 for i in range(1, 29)}}

CAS_CARTES = [
    {"nom": "Montant nul", "valeurs": {"montant": 0}},
    {"nom": "Temps hors plage", "valeurs": {"temps": 999999}},
    {"nom": "Montant négatif", "valeurs": {"montant": -3}},
    {"nom": "Classe invalide", "valeurs": {"classe": 3}},
]

CONTRATS = [
    ("contrats/operations.yaml", BASE_PAYSIM, CAS_PAYSIM),
    ("contrats/creditcard.yaml", BASE_CARTES, CAS_CARTES),
]


def charger():
    jeux = yaml.safe_load(JEUX.read_text(encoding="utf-8"))
    catalogue = json.loads(CATALOGUE.read_text(encoding="utf-8"))
    contrats = []
    for chemin, base, cas in CONTRATS:
        c = charger_contrat(chemin)
        c["fichier"] = chemin
        c["exemple"] = {"base": base, "cas": cas}
        c["champs_catalogue"] = catalogue["dictionnaires"][c["contrat"]["id"]]["champs"]
        rapport = Path(c["entree"]["rapport_json"])
        c["rapport"] = json.loads(rapport.read_text()) if rapport.exists() else None
        contrats.append(c)
    return {"jeux": jeux["jeux"], "sources": jeux["sources"], "contrats": contrats, "depot": DEPOT}


def construire():
    page = MODELE.read_text(encoding="utf-8").replace(
        "__DONNEES__", json.dumps(charger(), ensure_ascii=False, default=str)
    )
    entete = (
        '<!doctype html>\n<html lang="fr">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    )
    return entete + page.replace("</style>", "</style>\n</head>\n<body>", 1) + "\n</body>\n</html>\n"


def main():
    SORTIE.write_text(construire(), encoding="utf-8")
    print(f"{SORTIE} ecrit")


if __name__ == "__main__":
    main()
