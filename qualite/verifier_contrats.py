import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from qualite.contrat import charger_contrat

CONTRATS = ["contrats/operations.yaml", "contrats/creditcard.yaml"]
CLES_CONTRAT = {"id", "version", "statut", "description", "proprietaire", "consommateurs", "source", "fraicheur", "volumetrie", "retention", "evolution"}
CLES_ENTREE = {"fichier", "format", "cle", "cible", "silver", "quarantaine", "rapport_json", "rapport_md"}
TYPES_CHAMP = {"entier", "decimal", "texte"}
TYPES_REGLE = {"minimum", "plage", "valeurs", "format", "expression", "unicite"}
SEVERITES = {"erreur", "avertissement"}


def verifier(chemin):
    c = charger_contrat(chemin)
    problemes = []
    manquantes = CLES_CONTRAT - set(c.get("contrat", {}))
    if manquantes:
        problemes.append(f"cles du contrat manquantes: {sorted(manquantes)}")
    manquantes = CLES_ENTREE - set(c.get("entree", {}))
    if manquantes:
        problemes.append(f"cles d'entree manquantes: {sorted(manquantes)}")
    noms = [f["nom"] for f in c.get("champs", [])]
    if len(noms) != len(set(noms)):
        problemes.append("noms de champs en double")
    entree = c.get("entree", {})
    if entree.get("cle") not in noms:
        problemes.append("la cle d'entree n'est pas un champ")
    if entree.get("cible") not in noms:
        problemes.append("la cible n'est pas un champ")
    identifiants = []
    for f in c.get("champs", []):
        if f.get("type") not in TYPES_CHAMP:
            problemes.append(f"{f['nom']}: type inconnu")
        if not f.get("description") or not f.get("classification"):
            problemes.append(f"{f['nom']}: description ou classification manquante")
        for r in f.get("regles", []):
            identifiants.append(r["id"])
            if r["type"] not in TYPES_REGLE or r["severite"] not in SEVERITES:
                problemes.append(f"{r['id']}: type ou severite invalide")
            if r["type"] == "valeurs" and not f.get("valeurs"):
                problemes.append(f"{r['id']}: liste de valeurs absente")
            if r["type"] == "format" and not f.get("format"):
                problemes.append(f"{r['id']}: format absent")
    for r in c.get("regles_table", []):
        identifiants.append(r["id"])
        if r["severite"] not in SEVERITES or r["type"] not in TYPES_REGLE:
            problemes.append(f"{r['id']}: type ou severite invalide")
        for champ in r.get("champs", []):
            if champ not in noms:
                problemes.append(f"{r['id']}: champ inconnu {champ}")
    if len(identifiants) != len(set(identifiants)):
        problemes.append("identifiants de regles en double")
    seuil = c.get("qualite_globale", {}).get("taux_rejet_max")
    if seuil is None or not 0 < seuil < 1:
        problemes.append("taux_rejet_max absent ou hors de 0 et 1")
    return problemes


def main():
    echec = False
    for chemin in CONTRATS:
        problemes = verifier(chemin)
        print(f"{chemin}: {'conforme' if not problemes else 'non conforme'}")
        for p in problemes:
            print(f"  - {p}")
        echec = echec or bool(problemes)
    sys.exit(1 if echec else 0)


if __name__ == "__main__":
    main()
