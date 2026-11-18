from qualite.verifier_contrats import CONTRATS, verifier


def test_contrats_du_depot_valides():
    for chemin in CONTRATS:
        assert verifier(chemin) == []


def test_contrat_casse_detecte(tmp_path):
    source = open("contrats/operations.yaml", encoding="utf-8").read()
    casse = source.replace("severite: erreur", "severite: grave", 1).replace("id: R02", "id: R01", 1)
    chemin = tmp_path / "casse.yaml"
    chemin.write_text(casse, encoding="utf-8")
    problemes = verifier(str(chemin))
    assert any("invalide" in p for p in problemes)
    assert any("double" in p for p in problemes)
