import argparse
import hashlib
import hmac
import json
import sys
import time
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from commun.env import lire_env
from qualite.contrat import charger_contrat, etiqueter, evaluer, renommer_source, typer

CONTRATS = {
    "paysim": "contrats/operations.yaml",
    "creditcard": "contrats/creditcard.yaml",
}


def lire_sel():
    sel = lire_env("PSEUDO_SEL")
    if not sel or sel == "changeme":
        raise SystemExit("PSEUDO_SEL absent ou non modifie dans .env")
    return sel.encode()


def pseudonymiser(serie, sel):
    table = {v: hmac.new(sel, v.encode(), hashlib.sha256).hexdigest()[:16] for v in serie.unique()}
    return serie.map(table)


def lire_source(contrat):
    entree = contrat["entree"]
    if entree["format"] == "csv":
        df = pd.read_csv(entree["fichier"])
    elif entree["format"] == "arff":
        from scipy.io import arff

        donnees, _ = arff.loadarff(entree["fichier"])
        df = pd.DataFrame(donnees)
        for colonne in df.columns:
            if df[colonne].dtype == object:
                df[colonne] = df[colonne].str.decode("utf-8").astype(int)
    else:
        raise ValueError(f"format inconnu: {entree['format']}")
    df = renommer_source(df, contrat)
    df.insert(0, entree["cle"], range(1, len(df) + 1))
    return df


def nettoyer(df, contrat, sel=None):
    cle = contrat["entree"]["cle"]
    df = typer(df, contrat)
    if cle not in df.columns:
        df.insert(0, cle, range(1, len(df) + 1))
    resultats = evaluer(df, contrat)
    erreurs = etiqueter(df, resultats, "erreur")
    avertissements = etiqueter(df, resultats, "avertissement")
    rejet = erreurs != ""

    quarantaine = df[rejet].assign(regles_violees=erreurs[rejet])
    propre = df[~rejet].copy()
    propre["controles_qualite"] = avertissements[~rejet]
    if "destinataire" in propre.columns:
        propre["type_destinataire"] = propre["destinataire"].str[0].map({"C": "client", "M": "marchand"})
    if sel is not None:
        for champ in contrat["champs"]:
            if champ.get("pseudonymise"):
                propre[champ["nom"]] = pseudonymiser(propre[champ["nom"]], sel)
    return propre, quarantaine, resultats, erreurs, avertissements


def rapport(df, propre, quarantaine, resultats, contrat, duree):
    total = len(df)
    cible = contrat["entree"]["cible"]
    lignes = []
    for identifiant, (masque, severite, message) in resultats.items():
        nb = int(masque.sum())
        lignes.append(
            {
                "regle": identifiant,
                "severite": severite,
                "message": message,
                "lignes": nb,
                "dont_fraudes": int(df.loc[masque, cible].sum()) if nb else 0,
                "taux": nb / total,
            }
        )
    seuil = contrat["qualite_globale"]["taux_rejet_max"]
    taux_rejet = len(quarantaine) / total
    attendu = contrat["contrat"]["volumetrie"]["lignes_attendues"]
    return {
        "contrat": contrat["contrat"]["id"],
        "version_contrat": contrat["contrat"]["version"],
        "lignes_lues": total,
        "lignes_silver": len(propre),
        "lignes_quarantaine": len(quarantaine),
        "taux_rejet": taux_rejet,
        "seuil_rejet": seuil,
        "conforme": taux_rejet <= seuil,
        "lignes_attendues": attendu,
        "volume_conforme": total == attendu,
        "fraudes_lues": int(df[cible].sum()),
        "fraudes_silver": int(propre[cible].sum()),
        "duree_secondes": round(duree, 1),
        "regles": lignes,
    }


def espace(n):
    return f"{n:,}".replace(",", " ")


def ecrire_markdown(r, chemin):
    lignes = [
        "# Rapport de qualite des donnees",
        "",
        f"Contrat `{r['contrat']}` version {r['version_contrat']}.",
        "",
        "| Indicateur | Valeur |",
        "|---|---|",
        f"| Lignes lues | {espace(r['lignes_lues'])} |",
        f"| Lignes en silver | {espace(r['lignes_silver'])} |",
        f"| Lignes en quarantaine | {espace(r['lignes_quarantaine'])} |",
        f"| Taux de rejet | {r['taux_rejet']:.4%} (seuil {r['seuil_rejet']:.2%}) |",
        f"| Volume conforme au contrat | {'oui' if r['volume_conforme'] else 'non'} |",
        f"| Fraudes lues / conservees | {espace(r['fraudes_lues'])} / {espace(r['fraudes_silver'])} |",
        f"| Verdict | {'conforme' if r['conforme'] else 'non conforme'} |",
        "",
        "| Regle | Severite | Description | Lignes | Dont fraudes |",
        "|---|---|---|---|---|",
    ]
    for x in sorted(r["regles"], key=lambda x: x["regle"]):
        if x["lignes"] or x["severite"] == "avertissement" or x["regle"][1] == "2":
            lignes.append(
                f"| {x['regle']} | {x['severite']} | {x['message']} | {espace(x['lignes'])} | {espace(x['dont_fraudes'])} |"
            )
    Path(chemin).parent.mkdir(parents=True, exist_ok=True)
    Path(chemin).write_text("\n".join(lignes) + "\n", encoding="utf-8")


def executer(jeu):
    debut = time.time()
    contrat = charger_contrat(CONTRATS[jeu])
    entree = contrat["entree"]
    brut = lire_source(contrat)
    besoin_sel = any(c.get("pseudonymise") for c in contrat["champs"])
    propre, quarantaine, resultats, _, _ = nettoyer(brut, contrat, lire_sel() if besoin_sel else None)
    r = rapport(brut, propre, quarantaine, resultats, contrat, time.time() - debut)
    for chemin in (entree["silver"], entree["quarantaine"], entree["rapport_json"]):
        Path(chemin).parent.mkdir(parents=True, exist_ok=True)
    propre.to_parquet(entree["silver"], index=False)
    quarantaine.to_parquet(entree["quarantaine"], index=False)
    Path(entree["rapport_json"]).write_text(json.dumps(r, indent=2, default=str))
    ecrire_markdown(r, entree["rapport_md"])
    return r


def main():
    p = argparse.ArgumentParser()
    p.add_argument("jeux", nargs="*", choices=list(CONTRATS))
    for jeu in p.parse_args().jeux or list(CONTRATS):
        r = executer(jeu)
        print(jeu, {k: v for k, v in r.items() if k != "regles"})
        for x in r["regles"]:
            if x["lignes"]:
                print("  ", x["regle"], x["severite"], x["lignes"], "fraudes", x["dont_fraudes"])


if __name__ == "__main__":
    main()
