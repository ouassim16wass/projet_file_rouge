import argparse
import csv
import json
import time
from pathlib import Path

from confluent_kafka import Producer

COLONNES = {
    "step": ("pas", int),
    "type": ("type", str),
    "amount": ("montant", float),
    "nameOrig": ("emetteur", str),
    "oldbalanceOrg": ("solde_emetteur_avant", float),
    "newbalanceOrig": ("solde_emetteur_apres", float),
    "nameDest": ("destinataire", str),
    "oldbalanceDest": ("solde_destinataire_avant", float),
    "newbalanceDest": ("solde_destinataire_apres", float),
    "isFraud": ("est_fraude", int),
}


def convertir(numero, ligne):
    evenement = {"id_operation": numero}
    for source, (cible, cast) in COLONNES.items():
        evenement[cible] = cast(ligne[source])
    return evenement


def pas_de_temps(chemin, pas_max, depart):
    courant, lot = None, []
    with open(chemin, newline="") as f:
        for numero, ligne in enumerate(csv.DictReader(f), start=1):
            if numero <= depart:
                continue
            pas = int(ligne["step"])
            if pas_max and pas > pas_max:
                break
            if courant is not None and pas != courant:
                yield courant, lot
                lot = []
            courant = pas
            lot.append(convertir(numero, ligne))
    if lot:
        yield courant, lot


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--fichier", default="data/raw/paysim.csv")
    p.add_argument("--serveur", default="localhost:9092")
    p.add_argument("--topic", default="operations.brutes")
    p.add_argument("--secondes-par-pas", type=float, default=5.0)
    p.add_argument("--pas-max", type=int, default=0)
    p.add_argument("--depart", type=int, default=0)
    a = p.parse_args()

    producteur = Producer(
        {
            "bootstrap.servers": a.serveur,
            "enable.idempotence": True,
            "linger.ms": 20,
            "compression.type": "lz4",
            "queue.buffering.max.messages": 500000,
        }
    )
    total = 0
    for pas, lot in pas_de_temps(Path(a.fichier), a.pas_max, a.depart):
        debut = time.time()
        for evenement in lot:
            while True:
                try:
                    producteur.produce(
                        a.topic,
                        key=evenement["emetteur"],
                        value=json.dumps(evenement),
                    )
                    break
                except BufferError:
                    producteur.poll(0.1)
            producteur.poll(0)
        producteur.flush()
        total += len(lot)
        print(f"pas={pas} envoyes={len(lot)} total={total}", flush=True)
        reste = a.secondes_par_pas - (time.time() - debut)
        if reste > 0:
            time.sleep(reste)


if __name__ == "__main__":
    main()
