import os
from pathlib import Path


def lire_env(cle, defaut=None):
    valeur = os.environ.get(cle)
    if valeur:
        return valeur
    chemin = Path(".env")
    if chemin.exists():
        for ligne in chemin.read_text().splitlines():
            if ligne.startswith(f"{cle}="):
                return ligne.split("=", 1)[1].strip()
    return defaut
