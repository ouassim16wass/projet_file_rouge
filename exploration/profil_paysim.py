import json
import sys
from pathlib import Path

import pandas as pd

FICHIER = Path("data/raw/paysim.csv")
SORTIE = Path("data/processed/profil_paysim.json")
TOLERANCE = 0.01


def main():
    d = pd.read_csv(FICHIER)
    n = len(d)
    r = {"lignes": n, "colonnes": list(d.columns)}
    r["types_pandas"] = {c: str(t) for c, t in d.dtypes.items()}
    r["nuls"] = {c: int(v) for c, v in d.isna().sum().items()}
    r["doublons_exacts"] = int(d.duplicated().sum())
    r["doublons_cle_metier"] = int(d.duplicated(["step", "nameOrig", "nameDest", "amount"]).sum())
    r["stats"] = {
        c: {k: float(v) for k, v in d[c].describe().items()}
        for c in ["step", "amount", "oldbalanceOrg", "newbalanceOrig", "oldbalanceDest", "newbalanceDest"]
    }
    r["valeurs_type"] = d["type"].value_counts().to_dict()
    r["fraude_par_type"] = d.groupby("type")["isFraud"].agg(["sum", "count"]).astype(int).to_dict("index")
    r["isFraud"] = d["isFraud"].value_counts().to_dict()
    r["isFlaggedFraud"] = d["isFlaggedFraud"].value_counts().to_dict()
    r["flag_vs_fraude"] = int(((d.isFlaggedFraud == 1) & (d.isFraud == 1)).sum())

    r["montant_nul_ou_negatif"] = int((d.amount <= 0).sum())
    r["soldes_negatifs"] = {c: int((d[c] < 0).sum()) for c in ["oldbalanceOrg", "newbalanceOrig", "oldbalanceDest", "newbalanceDest"]}
    r["format_emetteur_invalide"] = int((~d.nameOrig.str.match(r"^C\d+$")).sum())
    r["format_dest_invalide"] = int((~d.nameDest.str.match(r"^[CM]\d+$")).sum())
    r["destinataire_marchand"] = int(d.nameDest.str.startswith("M").sum())
    r["emetteurs_distincts"] = int(d.nameOrig.nunique())
    r["destinataires_distincts"] = int(d.nameDest.nunique())

    ecart_emetteur = (d.oldbalanceOrg - d.amount - d.newbalanceOrig).abs()
    r["incoherence_solde_emetteur"] = int((ecart_emetteur > TOLERANCE).sum())
    credit = d["type"].isin(["CASH_IN"])
    ecart_credit = (d.oldbalanceOrg + d.amount - d.newbalanceOrig).abs()
    r["incoherence_solde_emetteur_cash_in"] = int((credit & (ecart_credit > TOLERANCE)).sum())
    r["incoherence_debit_hors_cash_in"] = int((~credit & (ecart_emetteur > TOLERANCE)).sum())
    ecart_dest = (d.oldbalanceDest + d.amount - d.newbalanceDest).abs()
    recoit = d["type"].isin(["TRANSFER", "CASH_OUT", "DEBIT"]) & d.nameDest.str.startswith("C")
    r["incoherence_solde_destinataire"] = int((recoit & (ecart_dest > TOLERANCE)).sum())
    r["destinataire_marchand_soldes_nuls"] = int(
        (d.nameDest.str.startswith("M") & (d.oldbalanceDest == 0) & (d.newbalanceDest == 0)).sum()
    )
    r["emetteur_solde_zero_avant"] = int((d.oldbalanceOrg == 0).sum())
    r["emetteur_solde_zero_avant_par_fraude"] = d[d.oldbalanceOrg == 0].groupby("isFraud").size().to_dict()
    r["auto_virement"] = int((d.nameOrig == d.nameDest).sum())
    r["montant_sup_solde"] = int((d.amount > d.oldbalanceOrg + TOLERANCE).sum())
    r["montant_sup_solde_hors_cash_in"] = int(((d.amount > d.oldbalanceOrg + TOLERANCE) & ~credit).sum())
    r["pas_manquants"] = int(743 - d.step.nunique())
    r["ops_par_pas"] = {"min": int(d.groupby("step").size().min()), "max": int(d.groupby("step").size().max())}
    r["montant_max_par_type"] = {k: float(v) for k, v in d.groupby("type").amount.max().items()}

    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(json.dumps(r, indent=2, default=str))
    json.dump(r, sys.stdout, indent=1, default=str)


if __name__ == "__main__":
    main()
