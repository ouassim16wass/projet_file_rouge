import json
import sys
from pathlib import Path

import pandas as pd
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from qualite.contrat import charger_contrat

JEUX = Path("catalogue/jeux_de_donnees.yaml")
SORTIE_MD = Path("docs/catalogue_donnees.md")
SORTIE_JSON = Path("catalogue/catalogue.json")


def statistiques(df, champ):
    nom = champ["nom"]
    serie = df[nom]
    s = {"nuls": int(serie.isna().sum()), "distincts": int(serie.nunique())}
    if champ["type"] in ("decimal", "entier"):
        s["min"] = float(serie.min())
        s["max"] = float(serie.max())
    return s


def espace(n):
    return f"{n:,}".replace(",", " ")


def espace_decimal(x):
    return f"{x:,.2f}".replace(",", " ")


def cellule(texte):
    return str(texte).replace("|", "/").replace("\n", " ")


def documenter(contrat, df, derives):
    champs = []
    for c in contrat["champs"]:
        if c["nom"] in df.columns:
            champs.append({**c, "stats": statistiques(df, c)})
    for d in derives:
        champs.append({**d, "regles": [], "stats": statistiques(df, {"nom": d["nom"], "type": d["type"]})})
    return champs


def section_dictionnaire(titre, contrat, champs, nb_lignes):
    md = [
        "",
        f"## {titre}",
        "",
        espace(nb_lignes) + f" lignes. Contrat `{contrat['contrat']['id']}` version {contrat['contrat']['version']}.",
        "",
        "| Champ | Type | Classification | Description | Regles | Min | Max | Distincts | Nuls |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for c in champs:
        st = c["stats"]
        regles = ", ".join(r["id"] for r in c.get("regles", [])) or "-"
        if c.get("unique"):
            regles += " unique"
        mini = espace_decimal(st["min"]) if "min" in st else "-"
        maxi = espace_decimal(st["max"]) if "max" in st else "-"
        md.append(
            f"| {c['nom']} | {c['type']} | {c['classification']} | {cellule(c['description'])} | {regles} | {mini} | {maxi} | {st['distincts']} | {st['nuls']} |"
        )
    return md


def section_regles(titre, contrat):
    md = ["", f"## Regles de qualite : {titre}", "", "| ID | Portee | Severite | Description |", "|---|---|---|---|"]
    for c in contrat["champs"]:
        for r in c.get("regles", []):
            md.append(f"| {r['id']} | {c['nom']} | {r['severite']} | {cellule(r.get('message', r['type']))} |")
    for r in contrat.get("regles_table", []):
        md.append(f"| {r['id']} | table | {r['severite']} | {cellule(r.get('message', r['nom']))} |")
    return md


def main():
    jeux = yaml.safe_load(JEUX.read_text(encoding="utf-8"))
    derives_operations = [
        {"nom": "type_destinataire", "type": "texte", "classification": "derive", "description": "client ou marchand, deduit du prefixe du compte destinataire."},
        {"nom": "controles_qualite", "type": "texte", "classification": "technique", "description": "Identifiants des regles d'avertissement declenchees, separes par des virgules."},
    ]
    derives_cartes = [derives_operations[1]]
    ensembles = [
        ("Dictionnaire D02 operations_propres", charger_contrat("contrats/operations.yaml"), derives_operations),
        ("Dictionnaire D09 creditcard_ulb", charger_contrat("contrats/creditcard.yaml"), derives_cartes),
    ]

    md = ["# Catalogue de donnees GuardPay", "", "Genere par `catalogue/generer_catalogue.py` a partir des contrats `contrats/*.yaml`, de `catalogue/jeux_de_donnees.yaml` et des statistiques mesurees sur le silver.", "", "## Sources", "", "| ID | Nom | Nature | Origine | Licence | URL |", "|---|---|---|---|---|---|"]
    for s in jeux["sources"]:
        md.append(f"| {s['id']} | {s['nom']} | {s['nature']} | {s['origine']} | {s['licence']} | {s['url']} |")
    md += ["", "## Jeux de donnees", "", "| ID | Nom | Couche | Stockage | Source | Cle | Frequence | Sensibilite | Retention | Statut |", "|---|---|---|---|---|---|---|---|---|---|"]
    for j in jeux["jeux"]:
        md.append(f"| {j['id']} | {j['nom']} | {j['couche']} | {cellule(j['stockage'])} | {cellule(j['source'])} | {j['cle']} | {j['frequence']} | {j['sensibilite']} | {j['retention']} | {j['statut']} |")

    sortie_json = {"jeux": jeux["jeux"], "sources": jeux["sources"], "dictionnaires": {}}
    for titre, contrat, derives in ensembles:
        df = pd.read_parquet(contrat["entree"]["silver"])
        champs = documenter(contrat, df, derives)
        sortie_json["dictionnaires"][contrat["contrat"]["id"]] = {"contrat": contrat["contrat"], "champs": champs}
        md += section_dictionnaire(titre, contrat, champs, len(df))
        md += section_regles(contrat["contrat"]["id"], contrat)
        rapport = Path(contrat["entree"]["rapport_json"])
        if rapport.exists():
            r = json.loads(rapport.read_text())
            verdict = "conforme" if r["conforme"] else "non conforme"
            md += ["", f"Derniere mesure : {espace(r['lignes_lues'])} lignes lues, {r['lignes_quarantaine']} en quarantaine, verdict {verdict}. Detail dans `{contrat['entree']['rapport_md']}`."]

    SORTIE_JSON.write_text(json.dumps(sortie_json, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    SORTIE_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    nb_champs = sum(len(v["champs"]) for v in sortie_json["dictionnaires"].values())
    print(f"{len(jeux['jeux'])} jeux, {nb_champs} champs documentes")


if __name__ == "__main__":
    main()
