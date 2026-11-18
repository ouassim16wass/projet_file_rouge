import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import psycopg

from commun.env import lire_env

SORTIE = Path("docs/mesures_couts.md")

FICHIERS = [
    ("Brut PaySim (CSV)", "data/raw/paysim.csv"),
    ("Brut ULB (ARFF)", "data/raw/creditcard.arff"),
    ("Silver operations (Parquet)", "data/processed/silver/operations.parquet"),
    ("Silver cartes (Parquet)", "data/processed/silver/transactions_cartes.parquet"),
    ("Gold variables (Parquet zstd)", "data/processed/gold/variables_operation.parquet"),
    ("Gold indicateurs (Parquet zstd)", "data/processed/gold/indicateurs_horaires.parquet"),
]


def mo(octets):
    return f"{octets / 1024 / 1024:,.1f}".replace(",", " ")


def taille(chemin):
    p = Path(chemin)
    if p.is_file():
        return p.stat().st_size
    return sum(f.stat().st_size for f in p.rglob("*") if f.is_file()) if p.exists() else 0


def tailles_postgres():
    with psycopg.connect(
        host=lire_env("POSTGRES_HOST", "localhost"),
        port=int(lire_env("POSTGRES_PORT", "5433")),
        user=lire_env("POSTGRES_USER"),
        password=lire_env("POSTGRES_PASSWORD"),
        dbname=lire_env("POSTGRES_DB"),
    ) as conn:
        cur = conn.execute(
            "SELECT relname, pg_total_relation_size(c.oid), pg_relation_size(c.oid) "
            "FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace "
            "WHERE n.nspname = 'gold' AND c.relkind = 'r' ORDER BY 2 DESC"
        )
        tables = cur.fetchall()
        cur = conn.execute(
            "SELECT table_cible, max(duree_secondes), max(charge_le) FROM gold.journal_chargement GROUP BY 1"
        )
        durees = cur.fetchall()
    return tables, durees


def conteneurs():
    sortie = subprocess.run(
        ["docker", "stats", "--no-stream", "--format", "{{.Name}}|{{.MemUsage}}|{{.CPUPerc}}"],
        capture_output=True,
        text=True,
    ).stdout
    return [ligne.split("|") for ligne in sortie.splitlines() if ligne.startswith("guardpay-")]


def main():
    brut = taille("data/raw/paysim.csv")
    lignes = ["# Mesures de couts", "", "Genere par `outils/mesurer_couts.py` sur la machine de developpement.", "", "## Stockage fichiers", "", "| Jeu | Taille (Mo) | Part du CSV PaySim |", "|---|---|---|"]
    for nom, chemin in FICHIERS:
        t = taille(chemin)
        lignes.append(f"| {nom} | {mo(t)} | {t / brut:.0%} |")
    tables, durees = tailles_postgres()
    lignes += ["", "## Stockage PostgreSQL (schema gold)", "", "| Table | Total avec index (Mo) | Donnees seules (Mo) |", "|---|---|---|"]
    for nom, total, donnees in tables:
        lignes.append(f"| {nom} | {mo(total)} | {mo(donnees)} |")
    lignes += ["", "## Duree de chargement", "", "| Table | Duree max (s) |", "|---|---|"]
    for nom, duree, _ in durees:
        lignes.append(f"| {nom} | {duree} |")
    lignes += ["", "## Ressources des conteneurs au repos", "", "| Conteneur | Memoire utilisee / limite | CPU |", "|---|---|---|"]
    for nom, mem, cpu in conteneurs():
        lignes.append(f"| {nom} | {mem} | {cpu} |")
    SORTIE.write_text("\n".join(lignes) + "\n", encoding="utf-8")
    print("\n".join(lignes))


if __name__ == "__main__":
    main()
