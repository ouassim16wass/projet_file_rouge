import io
import sys
import time
from pathlib import Path

import pandas as pd
import psycopg

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from commun.env import lire_env

GOLD = Path("data/processed/gold")
LOT = 200_000

TABLES = {
    "variables_operation": {"cle": ["id_operation"], "fichier": "variables_operation.parquet"},
    "indicateurs_horaires": {"cle": ["pas", "type"], "fichier": "indicateurs_horaires.parquet"},
}


def connexion():
    return psycopg.connect(
        host=lire_env("POSTGRES_HOST", "localhost"),
        port=int(lire_env("POSTGRES_PORT", "5433")),
        user=lire_env("POSTGRES_USER"),
        password=lire_env("POSTGRES_PASSWORD"),
        dbname=lire_env("POSTGRES_DB"),
    )


def charger_table(conn, nom, config):
    debut = time.time()
    df = pd.read_parquet(GOLD / config["fichier"])
    colonnes = list(df.columns)
    liste = ", ".join(colonnes)
    miseajour = ", ".join(f"{c} = EXCLUDED.{c}" for c in colonnes if c not in config["cle"])
    with conn.cursor() as cur:
        cur.execute(f"CREATE TEMP TABLE tampon (LIKE gold.{nom} INCLUDING DEFAULTS) ON COMMIT DROP")
        with cur.copy(f"COPY tampon ({liste}) FROM STDIN WITH (FORMAT csv, NULL '\\N')") as copie:
            for debut_lot in range(0, len(df), LOT):
                tampon = io.StringIO()
                df.iloc[debut_lot : debut_lot + LOT].to_csv(tampon, index=False, header=False, na_rep="\\N")
                copie.write(tampon.getvalue())
        cur.execute(
            f"INSERT INTO gold.{nom} ({liste}) SELECT {liste} FROM tampon "
            f"ON CONFLICT ({', '.join(config['cle'])}) DO UPDATE SET {miseajour}"
        )
        cur.execute(f"SELECT count(*) FROM gold.{nom}")
        en_base = cur.fetchone()[0]
        duree = round(time.time() - debut, 2)
        cur.execute(
            "INSERT INTO gold.journal_chargement (table_cible, lignes_lues, lignes_en_base, duree_secondes) "
            "VALUES (%s, %s, %s, %s)",
            (nom, len(df), en_base, duree),
        )
    conn.commit()
    print(f"{nom}: {len(df)} lignes lues, {en_base} en base, {duree} s")


def main():
    with connexion() as conn:
        for nom, config in TABLES.items():
            charger_table(conn, nom, config)


if __name__ == "__main__":
    main()
