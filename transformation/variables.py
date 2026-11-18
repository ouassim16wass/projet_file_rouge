import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

SILVER = Path("data/processed/silver/operations.parquet")
GOLD = Path("data/processed/gold")
TYPES_MODELE = ("TRANSFER", "CASH_OUT")
DERNIER_PAS_APPRENTISSAGE = 323
TOLERANCE = 0.01


def historique_destinataire(df):
    df = df.sort_values("id_operation")
    groupe = df.groupby("destinataire", sort=False)
    nb = groupe.cumcount()
    cumul = groupe["montant"].cumsum() - df["montant"]
    return nb.reindex(df.index), cumul.reindex(df.index)


def calculer_variables(silver):
    df = silver.copy()
    nb_recus, montant_recu = historique_destinataire(df)
    df["nb_recus_destinataire_avant"] = nb_recus.astype("int32")
    df["montant_recu_destinataire_avant"] = montant_recu.round(2)
    df["destinataire_inconnu"] = df["nb_recus_destinataire_avant"] == 0

    df = df[df["type"].isin(TYPES_MODELE)].copy()
    df["heure_du_jour"] = ((df["pas"] - 1) % 24).astype("int16")
    df["jour"] = ((df["pas"] - 1) // 24).astype("int16")
    df["ecart_solde_emetteur"] = (df["solde_emetteur_avant"] - df["montant"] - df["solde_emetteur_apres"]).round(2)
    df["ecart_solde_destinataire"] = (
        df["solde_destinataire_avant"] + df["montant"] - df["solde_destinataire_apres"]
    ).round(2)
    df["compte_vide_apres"] = (df["solde_emetteur_apres"] == 0) & (df["solde_emetteur_avant"] > 0)
    df["montant_egal_solde"] = (df["solde_emetteur_avant"] > 0) & (
        (df["montant"] - df["solde_emetteur_avant"]).abs() <= TOLERANCE
    )
    avant = df["solde_emetteur_avant"].where(df["solde_emetteur_avant"] > 0)
    df["part_solde_deplacee"] = (df["montant"] / avant).clip(upper=1000).replace([np.inf, -np.inf], np.nan)
    df["jeu_donnees"] = np.where(df["pas"] <= DERNIER_PAS_APPRENTISSAGE, "apprentissage", "test")

    colonnes = [
        "id_operation", "pas", "heure_du_jour", "jour", "type", "montant",
        "solde_emetteur_avant", "solde_emetteur_apres", "solde_destinataire_avant", "solde_destinataire_apres",
        "type_destinataire", "ecart_solde_emetteur", "ecart_solde_destinataire", "compte_vide_apres",
        "montant_egal_solde", "part_solde_deplacee", "nb_recus_destinataire_avant",
        "montant_recu_destinataire_avant", "destinataire_inconnu", "jeu_donnees", "est_fraude",
        "controles_qualite",
    ]
    return df[colonnes].sort_values("id_operation").reset_index(drop=True)


def calculer_indicateurs(silver):
    df = silver.copy()
    df["avertissement"] = df["controles_qualite"] != ""
    agg = (
        df.groupby(["pas", "type"])
        .agg(
            nb_operations=("id_operation", "size"),
            montant_total=("montant", "sum"),
            montant_moyen=("montant", "mean"),
            nb_fraudes=("est_fraude", "sum"),
            nb_avertissements=("avertissement", "sum"),
        )
        .reset_index()
    )
    agg["montant_total"] = agg["montant_total"].round(2)
    agg["montant_moyen"] = agg["montant_moyen"].round(2)
    agg["heure_du_jour"] = ((agg["pas"] - 1) % 24).astype("int16")
    return agg


def main():
    silver = pd.read_parquet(SILVER)
    GOLD.mkdir(parents=True, exist_ok=True)
    variables = calculer_variables(silver)
    indicateurs = calculer_indicateurs(silver)
    variables.to_parquet(GOLD / "variables_operation.parquet", index=False, compression="zstd")
    indicateurs.to_parquet(GOLD / "indicateurs_horaires.parquet", index=False, compression="zstd")
    print(f"variables_operation: {len(variables)} lignes, {int(variables.est_fraude.sum())} fraudes")
    print(f"indicateurs_horaires: {len(indicateurs)} lignes")
    print(variables.jeu_donnees.value_counts().to_dict())


if __name__ == "__main__":
    main()
