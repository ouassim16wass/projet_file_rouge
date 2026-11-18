import sys
import urllib.request
from pathlib import Path

SOURCES = {
    "paysim": (
        "https://huggingface.co/datasets/theman10/paysim/resolve/main/paysim.csv",
        "paysim.csv",
    ),
    "creditcard": (
        "https://openml.org/data/v1/download/1673544/creditcard.arff",
        "creditcard.arff",
    ),
}

DOSSIER = Path("data/raw")


def telecharger(nom):
    url, fichier = SOURCES[nom]
    DOSSIER.mkdir(parents=True, exist_ok=True)
    cible = DOSSIER / fichier
    if cible.exists():
        print(f"{nom}: deja present ({cible.stat().st_size} octets)")
        return
    requete = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(requete, timeout=60) as reponse, open(cible, "wb") as sortie:
        while True:
            bloc = reponse.read(1 << 20)
            if not bloc:
                break
            sortie.write(bloc)
    print(f"{nom}: telecharge ({cible.stat().st_size} octets)")


if __name__ == "__main__":
    noms = sys.argv[1:] or list(SOURCES)
    for nom in noms:
        telecharger(nom)
