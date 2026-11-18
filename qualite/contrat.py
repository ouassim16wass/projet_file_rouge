import re
from pathlib import Path

import pandas as pd
import yaml

CHEMIN_CONTRAT = Path("contrats/operations.yaml")


def charger_contrat(chemin=CHEMIN_CONTRAT):
    return yaml.safe_load(Path(chemin).read_text(encoding="utf-8"))


def renommer_source(df, contrat):
    table = {c["source"]: c["nom"] for c in contrat["champs"] if c["source"] != "genere"}
    return df.rename(columns=table)


def typer(df, contrat):
    df = df.copy()
    for champ in contrat["champs"]:
        nom = champ["nom"]
        if nom in df.columns and champ["type"] in ("decimal", "entier"):
            df[nom] = pd.to_numeric(df[nom], errors="coerce")
    return df


def _violations_champ(df, champ, regle):
    serie = df[champ["nom"]]
    genre = regle["type"]
    if genre == "minimum":
        return serie < regle["valeur"]
    if genre == "plage":
        return (serie < regle["min"]) | (serie > regle["max"])
    if genre == "valeurs":
        return ~serie.isin(champ["valeurs"])
    if genre == "format":
        return ~serie.astype(str).str.match(re.compile(champ["format"]))
    if genre == "expression":
        return df.eval(regle["violation"], engine="python").astype(bool)
    raise ValueError(f"type de regle inconnu: {genre}")


def _violations_table(df, regle):
    if regle["type"] == "unicite":
        return df.duplicated(regle["champs"], keep="first")
    if regle["type"] == "expression":
        return df.eval(regle["violation"], engine="python").astype(bool)
    raise ValueError(f"type de regle inconnu: {regle['type']}")


def evaluer(df, contrat):
    resultats = {}
    for champ in contrat["champs"]:
        if champ.get("obligatoire"):
            resultats[f"NUL_{champ['nom']}"] = (
                df[champ["nom"]].isna(),
                "erreur",
                f"{champ['nom']} manquant",
            )
        for regle in champ.get("regles", []):
            resultats[regle["id"]] = (
                _violations_champ(df, champ, regle).fillna(False),
                regle["severite"],
                regle.get("message", f"{champ['nom']} {regle['type']}"),
            )
    for regle in contrat.get("regles_table", []):
        resultats[regle["id"]] = (
            _violations_table(df, regle).fillna(False),
            regle["severite"],
            regle.get("message", regle["nom"]),
        )
    return resultats


def etiqueter(df, resultats, severite):
    etiquettes = pd.Series("", index=df.index, dtype="object")
    for identifiant, (masque, sev, _) in resultats.items():
        if sev != severite or not masque.any():
            continue
        etiquettes = etiquettes.where(~masque, etiquettes + identifiant + ",")
    return etiquettes.str.rstrip(",")
