import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from qualite.contrat import charger_contrat

CONTRATS = ["contrats/operations.yaml", "contrats/creditcard.yaml"]
SORTIE = Path("docs/contrats_donnees.md")


def cellule(texte):
    return str(texte).replace("|", "/").replace("\n", " ")


def espace(n):
    return f"{n:,}".replace(",", " ")


def regle_lisible(champ, regle):
    genre = regle["type"]
    if genre == "minimum":
        return f"valeur au moins {regle['valeur']}"
    if genre == "plage":
        return f"entre {regle['min']} et {regle['max']}"
    if genre == "valeurs":
        return "valeur parmi " + ", ".join(str(v) for v in champ["valeurs"])
    if genre == "format":
        return f"format `{champ['format']}`"
    return regle.get("message", regle["violation"])


def section(chemin):
    c = charger_contrat(chemin)
    m = c["contrat"]
    md = [
        f"## {m['id']} version {m['version']}",
        "",
        f"Fichier : [`{chemin}`](../{chemin}). Statut : {m['statut']}. Jeu de donnees : {m['jeu_de_donnees']}.",
        "",
        m["description"],
        "",
        "### Engagements",
        "",
        "| Element | Engagement |",
        "|---|---|",
        f"| Proprietaire | {m['proprietaire']} |",
        f"| Consommateurs | {', '.join(m['consommateurs'])} |",
        f"| Source | {m['source']['nom']}, {m['source']['origine']}, {m['source']['nature']} |",
        f"| Licence | {m['source']['licence']} |",
        f"| Livraison | {m['fraicheur']['livraison']} |",
    ]
    if "delai_max_ingestion_secondes" in m["fraicheur"]:
        md.append(f"| Delai maximal d'ingestion | {m['fraicheur']['delai_max_ingestion_secondes']} secondes |")
    md += [
        f"| Volume attendu | {espace(m['volumetrie']['lignes_attendues'])} lignes |",
        f"| Taux de rejet maximal | {c['qualite_globale']['taux_rejet_max']:.2%} |",
        f"| Conservation | {m['retention']} |",
        f"| Evolution | {m['evolution']['compatibilite']} |",
        f"| Notification | {m['evolution']['notification']} |",
        "",
        "### Traitement des anomalies",
        "",
        f"- Erreur : {c['qualite_globale']['actions']['erreur']}.",
        f"- Avertissement : {c['qualite_globale']['actions']['avertissement']}.",
        "",
        "### Champs",
        "",
        "| Champ | Source | Type | Obligatoire | Classification | Description | Regles |",
        "|---|---|---|---|---|---|---|",
    ]
    for ch in c["champs"]:
        regles = "; ".join(f"{r['id']} ({r['severite']}) {regle_lisible(ch, r)}" for r in ch.get("regles", [])) or "-"
        if ch.get("pseudonymise"):
            regles += "; pseudonymise"
        md.append(
            f"| {ch['nom']} | {ch['source']} | {ch['type']} | {'oui' if ch.get('obligatoire') else 'non'} | {ch['classification']} | {cellule(ch['description'])} | {cellule(regles)} |"
        )
    md += ["", "### Regles portant sur la table", "", "| ID | Nom | Severite | Description |", "|---|---|---|---|"]
    for r in c.get("regles_table", []):
        md.append(f"| {r['id']} | {r['nom']} | {r['severite']} | {cellule(r.get('message', r['nom']))} |")
    md.append("")
    return md


def main():
    md = [
        "# Contrats de donnees GuardPay",
        "",
        "Page generee par `catalogue/generer_contrats.py` a partir des fichiers `contrats/*.yaml`, qui font reference.",
        "Chaque contrat fixe le schema, les regles de qualite, la fraicheur, la conservation et les conditions d'evolution entre le producteur et les consommateurs.",
        "",
    ]
    for chemin in CONTRATS:
        md += section(chemin)
    SORTIE.write_text("\n".join(md), encoding="utf-8")
    print(f"{SORTIE} : {len(CONTRATS)} contrats")


if __name__ == "__main__":
    main()
