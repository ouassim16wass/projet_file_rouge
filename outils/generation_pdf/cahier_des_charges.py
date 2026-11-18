from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
                                Table, TableStyle, PageBreak, KeepTogether)

OUT = "docs/GuardPay_cas_usage_cahier_des_charges.pdf"
TITRE = "GuardPay - Cas d'usage et cahier des charges"

NAVY = colors.HexColor("#14325c")
TEAL = colors.HexColor("#1f7a8c")
LIGHT = colors.HexColor("#eaf1f7")
GREY = colors.HexColor("#555555")

ss = getSampleStyleSheet()
body = ParagraphStyle("body", parent=ss["Normal"], fontName="Helvetica", fontSize=9.5, leading=13.5, spaceAfter=5)
small = ParagraphStyle("small", parent=body, fontSize=8.3, leading=11, spaceAfter=0)
smallb = ParagraphStyle("smallb", parent=small, fontName="Helvetica-Bold", textColor=colors.white)
h1 = ParagraphStyle("h1", parent=body, fontName="Helvetica-Bold", fontSize=15, leading=19, textColor=NAVY,
                    spaceBefore=14, spaceAfter=7, keepWithNext=1)
h2 = ParagraphStyle("h2", parent=body, fontName="Helvetica-Bold", fontSize=11.2, leading=15, textColor=TEAL,
                    spaceBefore=9, spaceAfter=4, keepWithNext=1)
bullet = ParagraphStyle("bullet", parent=body, leftIndent=14, bulletIndent=3, spaceAfter=2.5)
title = ParagraphStyle("title", parent=body, fontName="Helvetica-Bold", fontSize=30, leading=36, textColor=NAVY, alignment=TA_CENTER)
subtitle = ParagraphStyle("subtitle", parent=body, fontSize=14, leading=19, textColor=TEAL, alignment=TA_CENTER)
cover = ParagraphStyle("cover", parent=body, fontSize=10.5, leading=15, textColor=GREY, alignment=TA_CENTER)
mono = ParagraphStyle("mono", parent=small, fontName="Courier", fontSize=7.8, leading=10)


def P(t, s=body):
    return Paragraph(t, s)


def B(items):
    return [Paragraph(i, bullet, bulletText="•") for i in items]


def tbl(rows, widths, header=True):
    data = []
    for ri, row in enumerate(rows):
        st = smallb if (header and ri == 0) else small
        data.append([Paragraph(str(c), st) for c in row])
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    style = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#b8c4d0")),
        ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    if header:
        style.append(("BACKGROUND", (0, 0), (-1, 0), NAVY))
    for i in range(1 if header else 0, len(rows)):
        if i % 2 == 0:
            style.append(("BACKGROUND", (0, i), (-1, i), LIGHT))
    t.setStyle(TableStyle(style))
    return t


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(GREY)
    canvas.drawString(2 * cm, 1.2 * cm, "GuardPay - Cas d'usage et cahier des charges")
    canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, "Page %d" % doc.page)
    canvas.setStrokeColor(colors.HexColor("#b8c4d0"))
    canvas.line(2 * cm, 1.6 * cm, A4[0] - 2 * cm, 1.6 * cm)
    canvas.restoreState()


doc = BaseDocTemplate(OUT, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=2 * cm,
                      bottomMargin=2.2 * cm, title=TITRE, author="",
                      subject="Projet fil rouge - Titre RNCP Data Engineer")
frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="f")
doc.addPageTemplates([PageTemplate(id="p", frames=[frame], onPage=footer)])
W = doc.width
s = []

s += [Spacer(1, 4.3 * cm), P("GuardPay", title), Spacer(1, 0.4 * cm),
      P("Détection de fraude en temps réel sur les opérations d'une banque", subtitle),
      Spacer(1, 1.2 * cm),
      P("Cas d'usage et cahier des charges", ParagraphStyle("c2", parent=subtitle, fontName="Helvetica-Bold", textColor=NAVY)),
      Spacer(1, 2.2 * cm),
      P("Projet fil rouge - Titre RNCP Data Engineer (RNCP42655)", cover),
      P("Version 1.0 - 18 novembre 2026", cover),
      P("Statut : document de cadrage, à valider", cover),
      Spacer(1, 2.3 * cm)]
s.append(tbl([
    ["Bloc", "Intitulé", "Traitement dans ce document"],
    ["BC01", "Concevoir l'architecture", "Besoin, problématique, périmètre, exigences, choix techniques, conformité"],
    ["BC02", "Développer l'architecture", "Sources, préparation, catalogue, stockage SQL et NoSQL, modèle de détection"],
    ["BC03", "Déployer avec IA", "Flux, API, conteneurs, orchestration, CI/CD, monitoring"],
    ["BC04", "Piloter le projet", "Planning, jalons, risques, indicateurs, recette"],
], [1.6 * cm, 5 * cm, W - 6.6 * cm]))
s.append(PageBreak())

s += [P("1. Le cas d'usage en bref", h1),
      P("La Banque Aurore (fictive) propose la banque en ligne à ses clients : virements, retraits, versements et paiements. "
        "Sa direction de la lutte contre la fraude doit repérer les opérations frauduleuses au moment où elles se produisent, "
        "sans bloquer par erreur les clients honnêtes. Le projet <b>GuardPay</b> construit la plateforme de données qui reçoit les "
        "opérations en continu, calcule un score de risque explicable pour chacune, et met les alertes à disposition des analystes "
        "par API et tableau de bord."),
      P("<b>Commanditaire (fictif) :</b> la direction de la lutte contre la fraude de la Banque Aurore. Les opérations sont "
        "des données publiques de substitution : l'une est synthétique, l'autre réelle mais anonymisée. Ce choix est assumé "
        "dans le mémoire comme une hypothèse de travail."),
      P("2. Contexte et problématique", h1),
      P("Pour une banque, la fraude se traduit par trois coûts : les pertes financières directes, les clients honnêtes bloqués par "
        "de fausses alertes, et le temps des analystes noyés sous des alertes sans priorité. Les systèmes historiques reposent "
        "sur des règles fixes. Sur le jeu de données retenu, la règle de signalement existante n'a repéré que 16 fraudes sur "
        "8 213, soit 0,19 %."),
      P("Le cadre européen des services de paiement (DSP2) impose aux prestataires des dispositifs de surveillance des opérations. "
        "Le RGPD encadre les décisions entièrement automatisées. Les références exactes sont à vérifier dans les textes officiels "
        "avant citation dans le mémoire. Dans ce projet, le score est une <b>aide à la décision</b> : l'analyste garde la main."),
      P("Problématique", h2),
      Table([[P("<b>Comment détecter en temps réel les opérations frauduleuses d'une banque, avec un score explicable et un taux de "
                "fausses alertes maîtrisé, sur une plateforme de données fiable, observable et déployable ?</b>",
                ParagraphStyle("q", parent=body, textColor=NAVY))]], colWidths=[W],
            style=TableStyle([("BACKGROUND", (0, 0), (-1, -1), LIGHT), ("BOX", (0, 0), (-1, -1), 1, TEAL),
                              ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                              ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))]

s += [P("3. Besoin métier", h1),
      tbl([["Profil", "Besoin", "Usage de la plateforme"],
           ["Analyste fraude", "Traiter en priorité les alertes les plus probables et comprendre pourquoi une opération est suspecte",
            "File d'alertes classée par score, raisons de l'alerte, dossier d'investigation"],
           ["Responsable lutte contre la fraude", "Suivre les pertes évitées, le volume d'alertes et le taux de fausses alertes",
            "Tableau de bord par heure, par type d'opération, par montant"],
           ["Data Engineer", "Faire vivre la plateforme, rejouer un historique, déployer une nouvelle version du modèle",
            "Surveille les flux, relance un rejeu, suit les expériences et la dérive"]],
          [3.6 * cm, 6.8 * cm, W - 10.4 * cm]),
      P("User stories", h2),
      tbl([["Réf.", "En tant que ...", "Je veux ...", "Afin de ..."],
           ["US1", "Analyste", "voir les opérations suspectes classées par score avec les 3 raisons principales", "traiter d'abord les cas les plus probables"],
           ["US2", "Analyste", "enregistrer ma décision (fraude confirmée, fausse alerte) sur un dossier", "alimenter le réentraînement"],
           ["US3", "Responsable fraude", "suivre le nombre d'alertes et les montants à risque heure par heure", "ajuster les moyens humains"],
           ["US4", "Service d'autorisation", "obtenir le score d'une opération en moins de 100 ms par API", "décider avant la validation"],
           ["US5", "Data Engineer", "rejouer un mois d'opérations sans créer de doublons ni perdre d'événements", "récupérer après une panne"]],
          [1.2 * cm, 3.4 * cm, 7.2 * cm, W - 11.8 * cm])]

s += [P("4. Objectifs", h1), P("Objectif général", h2),
      P("Fournir à la direction de la lutte contre la fraude un score de risque temps réel, explicable et mesuré en coût, "
        "reposant sur une plateforme de données robuste."),
      P("Objectifs spécifiques", h2),
      tbl([["#", "Objectif", "Indicateur", "Bloc"],
           ["O1", "Ingérer les opérations en continu sans perte ni doublon",
            "6 362 620 opérations rejouées, comptage identique en entrée et en bronze, 0 doublon après reprise", "BC02/03"],
           ["O2", "Préparer et fiabiliser les données", "Rapport de qualité par exécution, opérations invalides en quarantaine, catalogue complet", "BC02"],
           ["O3", "Détecter la fraude mieux que les règles existantes",
            "Sur PaySim : au moins égal à la règle « montant égal au solde ». Sur ULB : AUC-PR et rappel à taux de fausses alertes fixé supérieurs à la régression logistique", "BC02/03"],
           ["O4", "Servir, orchestrer, déployer et surveiller",
            "API sous 100 ms, DAGs Airflow, 1 commande de démarrage, CI verte, monitoring actif", "BC03"],
           ["O5", "Cadrer et piloter", "Cahier des charges, planning, budget et écarts, KPI, plan de formation", "BC01/04"]],
          [1.0 * cm, 5.4 * cm, W - 8.2 * cm, 1.8 * cm]),
      P("Hypothèses à vérifier", h2)] + B([
    "<b>H1 :</b> sur PaySim, un modèle égale la règle « montant égal au solde » (97,5 % de rappel sans fausse alerte) et détecte une partie des 205 fraudes qu'elle manque. Sur ULB, il bat une régression logistique.",
    "<b>H2 :</b> les variables de solde (montant rapporté au solde, compte vidé, solde du destinataire nul) portent l'essentiel du signal sur PaySim. À vérifier avec SHAP.",
    "<b>H3 :</b> l'architecture Kafka et Spark absorbe un rejeu à 5 secondes par pas de temps (moyenne d'environ 1 700 événements par seconde, pic d'environ 10 300) sans perte ni doublon."])

s += [P("5. Périmètre", h1), P("Inclus", h2)] + B([
    "Rejeu d'opérations dans Kafka, traitement en flux avec PySpark, couches bronze, silver et gold.",
    "Entrepôt PostgreSQL (scores, indicateurs) et MongoDB (alertes, dossiers d'investigation).",
    "Modèle de détection, explication des alertes, suivi avec MLflow, réentraînement planifié.",
    "API de scoring, tableau de bord, orchestration, conteneurs, CI/CD, monitoring, catalogue de données."]) + [P("Exclus", h2)] + B([
    "Blocage réel d'un paiement : la plateforme émet des scores et des alertes, elle ne bloque rien.",
    "Authentification forte des clients, données personnelles réelles, apprentissage profond.",
    "Hébergement sur un cloud payant : tout tourne en local, seule l'API de démonstration peut être publiée."])

s += [P("6. Sources de données et URL", h1),
      P("Sources testées le 18 novembre 2026 : elles se téléchargent sans compte. Le script ingestion/telecharger_donnees.py les "
        "récupère dans data/raw, dossier exclu du dépôt.")]
src = [["#", "Source", "Contenu", "Format et volume", "URL"],
       ["S1", "PaySim (copie Hugging Face)",
        "Opérations bancaires simulées à partir de journaux réels d'un service de paiement mobile : virements, retraits, versements, paiements, débits. "
        "Étiquette de fraude. Source d'origine : Lopez-Rojas et al., PaySim (Kaggle, ealaxi/paysim1). Le fichier ci-contre est une copie hébergée sur Hugging Face. Licence à vérifier à la source d'origine.",
        "CSV de 494 Mo, 6 362 620 lignes, 11 colonnes, 743 pas de temps horaires (environ 31 jours)",
        "https://huggingface.co/datasets/theman10/paysim/resolve/main/paysim.csv"],
       ["S2", "Fraude carte ULB (OpenML)",
        "Transactions réelles de porteurs de cartes européens sur deux jours de septembre 2013. 28 variables anonymisées par ACP, heure, montant, étiquette.",
        "ARFF, 284 807 transactions, 492 fraudes (0,172 %)",
        "https://openml.org/data/v1/download/1673544/creditcard.arff"],
       ["S3", "Marketing bancaire (UCI, optionnel)", "Clients d'une banque portugaise. Utile pour une extension (segmentation).", "ZIP de 1 Mo",
        "https://archive.ics.uci.edu/static/public/222/bank+marketing.zip"]]
s.append(tbl(src, [0.9 * cm, 2.8 * cm, 5.6 * cm, 3.4 * cm, W - 12.7 * cm]))
s += [P("Ce que les données apprennent, mesuré sur le fichier complet", h2),
      tbl([["Constat", "Valeur mesurée", "Conséquence pour le projet"],
           ["Fraudes", "8 213 sur 6 362 620 (0,129 %)", "Classes très déséquilibrées : on n'utilise pas la précision globale"],
           ["Types concernés", "Fraudes uniquement dans TRANSFER (4 097) et CASH_OUT (4 116)", "Les 3 autres types n'ont aucune fraude"],
           ["Règle existante", "16 opérations signalées, 16 fraudes", "Rappel de 0,19 % : la référence à battre est très basse"],
           ["Règle « vide le compte »", "8 012 fraudes (97,6 %) mais 1 180 062 opérations légitimes signalées : précision de 0,67 %",
            "Règle naïve inutilisable seule : trop de fausses alertes"],
           ["Règle « montant égal au solde »", "8 008 fraudes (97,5 %), 0 opération légitime signalée",
            "Signal quasi trivial : PaySim valide la plateforme, ULB valide le modèle"],
           ["Destinataire à solde nul", "4 076 fraudes pour 1 706 opérations légitimes",
            "Variable utile, notamment pour les 205 fraudes manquées par la règle précédente"],
           ["Charge par pas de temps", "Moyenne 8 563 opérations, maximum 51 352 (pas 19)",
            "Le pic compte pour dimensionner Kafka et Spark, pas la moyenne"],
           ["Unicité", "0 doublon sur (pas, émetteur, destinataire, montant)",
            "Un id_operation (numéro de ligne) est tout de même ajouté comme clé d'idempotence"],
           ["Comptes émetteurs", "6 353 307 distincts, 3 opérations maximum par compte", "Pas d'historique par client : les variables de fréquence par client sont inutiles"],
           ["Comptes destinataires", "2 722 362 distincts, 459 658 vus plus d'une fois", "Les variables de fréquence côté destinataire sont exploitables"]],
          [3.2 * cm, 6.4 * cm, W - 9.6 * cm]),
      P("Les types d'opération PaySim sont ceux d'un service de paiement mobile, pas ceux de cartes. Dans le cas d'usage, ils représentent les "
        "virements, retraits, versements et paiements de la banque en ligne. Le jeu S2 apporte le point de vue carte bancaire réel.", small)]

s += [P("7. Exigences", h1), P("Fonctionnelles", h2),
      tbl([["Réf.", "Exigence", "Priorité", "Bloc"],
           ["EF1", "Rejouer les opérations dans le topic Kafka operations.brutes avec une vitesse réglable (1 pas de temps = N secondes). Chaque opération reçoit un id_operation (numéro de ligne du fichier).", "Haute", "BC02/03"],
           ["EF2", "Valider chaque opération (schéma, valeurs) et envoyer les invalides dans operations.rejetees.", "Haute", "BC02"],
           ["EF3", "Conserver les opérations brutes en bronze et produire une couche silver nettoyée.", "Haute", "BC02"],
           ["EF4", "Calculer les variables en flux : écarts de solde, compte vidé, heure, fréquence côté destinataire sur 1 h et 24 h.", "Haute", "BC02"],
           ["EF5", "Attribuer un score de risque à chaque opération et enregistrer les scores dans PostgreSQL.", "Haute", "BC02/03"],
           ["EF6", "Créer une alerte dans MongoDB au-dessus d'un seuil, avec les raisons de l'alerte.", "Haute", "BC02/03"],
           ["EF7", "Exposer POST /score : score et raisons pour une opération. Exposer GET /alertes : file priorisée.", "Haute", "BC03"],
           ["EF8", "Enregistrer la décision de l'analyste sur un dossier d'investigation.", "Moyenne", "BC03"],
           ["EF9", "Fournir un tableau de bord : alertes par heure, montants à risque, taux de fausses alertes.", "Haute", "BC03"],
           ["EF10", "Entraîner, évaluer et versionner le modèle avec MLflow. Réentraîner via Airflow.", "Haute", "BC02/03"],
           ["EF11", "Maintenir un catalogue de données à jour (dictionnaire, lignage, sensibilité).", "Haute", "BC02"]],
          [1.2 * cm, W - 5.6 * cm, 2 * cm, 2.4 * cm]),
      P("Non fonctionnelles", h2),
      tbl([["Catégorie", "Exigence"],
           ["Performance", "Rejeu à vitesse réglable. À 5 secondes par pas de temps : environ 1 700 événements par seconde en moyenne, pic d'environ 10 300, durée d'environ 1 heure. API sous 100 ms au 95e centile en local."],
           ["Fiabilité", "Checkpoints Spark, offsets Kafka, écritures idempotentes : un redémarrage ne crée ni perte ni doublon."],
           ["Portabilité", "Chaque service est conteneurisé, un seul docker compose up démarre l'ensemble."],
           ["Sécurité", "Secrets en variables d'environnement, images minimales, utilisateurs non root, bases accessibles seulement sur le réseau interne."],
           ["Observabilité", "Journaux structurés, métriques Prometheus, tableaux Grafana, suivi des expériences et de la dérive dans MLflow."],
           ["Maintenabilité", "Tests avec couverture visée de 70 %, CI/CD GitHub Actions, README d'architecture."],
           ["Sobriété", "Parquet, lecture incrémentale, réentraînement seulement quand la dérive le justifie."]],
          [3 * cm, W - 3 * cm])]

arch_head = [P("8. Architecture cible", h1),
             P("Les opérations sont rejouées dans Kafka, traitées en continu par PySpark, stockées en couches, notées par le modèle puis "
               "servies par une API et un tableau de bord. Airflow orchestre le réentraînement et les contrôles.")]
layers = [("Sources", "PaySim (opérations, rejouées en flux)  |  ULB (carte, validation du modèle)", "#d9e6f2"),
          ("Rejeu (Python)", "Producteur Kafka à vitesse réglable : un pas de temps horaire est rejoué en N secondes", "#c5dbea"),
          ("Kafka", "Topics : operations.brutes  |  operations.rejetees  |  alertes", "#a9cde0"),
          ("PySpark Structured Streaming", "Validation, déduplication, variables par fenêtres, appel du modèle, checkpoints", "#8dbfd6"),
          ("Stockage", "Bronze et silver Parquet  |  Gold PostgreSQL (scores, indicateurs)  |  MongoDB (alertes, dossiers, rejets)", "#6fb0c9"),
          ("Machine learning", "Entraînement, évaluation, MLflow (suivi, registre), SHAP", "#8dbfd6"),
          ("Services", "FastAPI (score, alertes)  |  Tableau de bord Grafana", "#a9cde0"),
          ("Transverse", "Airflow  |  Prometheus et Grafana  |  Docker Compose  |  GitHub Actions", "#d9e6f2")]
dt = Table([[Paragraph("<b>%s</b>" % a, small), Paragraph(b, small)] for a, b, _ in layers], colWidths=[3.6 * cm, W - 3.6 * cm])
dst = [("GRID", (0, 0), (-1, -1), 0.6, colors.white), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
       ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7), ("LEFTPADDING", (0, 0), (-1, -1), 8)]
for i, (_, _, c) in enumerate(layers):
    dst.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor(c)))
dt.setStyle(TableStyle(dst))
s.append(KeepTogether(arch_head + [dt, P("Figure 1 - Architecture en couches.", small)]))
s += [Spacer(1, 6), P("Choix technologiques", h2),
      tbl([["Besoin", "Choix", "Justification"],
           ["Flux d'événements", "Apache Kafka", "Rejeu de l'historique, découplage, reprise par offsets"],
           ["Traitement en continu", "PySpark Structured Streaming", "Fenêtres de temps, état par destinataire, checkpoints, volume"],
           ["Entrepôt relationnel", "PostgreSQL", "Scores et indicateurs, requêtes analytiques, tableau de bord"],
           ["Documents", "MongoDB", "Alertes et dossiers d'investigation au contenu évolutif (raisons, décisions, historique)"],
           ["Orchestration", "Apache Airflow", "Réentraînement, rapports de qualité, rejeu, relances"],
           ["API", "FastAPI", "Typage, documentation automatique, faible latence"],
           ["Modèle et suivi", "scikit-learn, LightGBM, MLflow, SHAP", "Référence lisible, modèle performant, suivi et explication"],
           ["Conteneurs et CI/CD", "Docker Compose, GitHub Actions", "Reproductibilité, tests et images automatisés"],
           ["Monitoring", "Prometheus, Grafana", "Métriques techniques et métier"]],
          [3.6 * cm, 4.6 * cm, W - 8.2 * cm])]

s += [P("9. Préparation des données et catalogue", h1), P("Chaîne de préparation", h2)] + B([
    "<b>Bronze :</b> opérations brutes telles que reçues de Kafka, horodatées, jamais modifiées.",
    "<b>Silver :</b> typage, contrôles, déduplication, pseudonymisation des identifiants de comptes par hachage salé. Les invalides vont en quarantaine.",
    "<b>Gold :</b> variables de l'opération, scores, indicateurs horaires, alertes."]) + [
      P("Règles de qualité", h2)] + B([
    "Type d'opération dans la liste PAYMENT, TRANSFER, CASH_OUT, DEBIT, CASH_IN.",
    "Montant strictement positif, soldes positifs ou nuls, pas de temps entre 1 et 743.",
    "Étiquette de fraude égale à 0 ou 1. id_operation unique, utilisé comme clé d'idempotence des écritures.",
    "Cohérence des soldes mesurée par un écart de solde, conservé comme variable et non comme rejet.",
    "Taux de rejet par exécution suivi dans un rapport, alerte au-delà d'un seuil."]) + [
      P("Catalogue de données", h2),
      P("Le catalogue est le référentiel unique des jeux de données : stocké dans le schéma catalog de PostgreSQL et exporté en fichiers YAML "
        "versionnés. Le DAG catalog_refresh met à jour volumes, fraîcheur et taux de rejet. Les durées de conservation sont proposées et "
        "seront validées dans l'analyse RGPD."),
      tbl([["ID", "Jeu de données", "Couche et stockage", "Source", "Clé", "Fréq.", "Sensibilité", "Rétention"],
           ["D01", "operations_brutes", "Kafka + Bronze Parquet", "S1", "id_operation", "Continue", "Moyenne", "1 an"],
           ["D02", "operations_propres", "Silver Parquet", "D01", "id_operation", "Continue", "Moyenne", "1 an"],
           ["D03", "variables_operation", "Gold PostgreSQL", "D02", "id_operation", "Continue", "Moyenne", "Par version du modèle"],
           ["D04", "scores_operations", "Gold PostgreSQL", "D03, modèle", "id_operation", "Continue", "Moyenne", "2 ans"],
           ["D05", "alertes", "MongoDB", "D04", "id_alerte", "Continue", "Moyenne", "2 ans"],
           ["D06", "dossiers_investigation", "MongoDB", "D05", "id_dossier", "À la décision", "Moyenne", "5 ans"],
           ["D07", "operations_rejetees", "Kafka + MongoDB", "D01", "id", "Continue", "Faible", "90 jours"],
           ["D08", "indicateurs_horaires", "Gold PostgreSQL", "D02, D04", "heure + type", "Horaire", "Faible", "Durée du service"],
           ["D09", "creditcard_ulb", "Silver Parquet + PostgreSQL", "S2", "ligne", "Statique", "Faible", "Durée du projet"],
           ["D10", "modeles", "MLflow (registre)", "Entraînement", "version", "À chaque entraînement", "Faible", "Toutes versions"]],
          [0.9 * cm, 3.5 * cm, 3 * cm, 2.1 * cm, 2.5 * cm, 1.6 * cm, 1.8 * cm, W - 15.4 * cm]),
      P("Dictionnaire de données - D01 (colonnes de PaySim vérifiées sur le fichier)", small),
      Spacer(1, 3),
      tbl([["Champ", "Type", "Description", "Règle de qualité"],
           ["id_operation", "entier", "Numéro de ligne du fichier, ajouté à l'ingestion", "Unique, non nul"],
           ["step", "entier", "Pas de temps horaire (1 = première heure)", "Entre 1 et 743"],
           ["type", "texte", "PAYMENT, TRANSFER, CASH_OUT, DEBIT, CASH_IN", "Dans la liste de valeurs"],
           ["amount", "décimal", "Montant de l'opération", "Strictement positif"],
           ["nameOrig", "texte", "Compte émetteur (pseudonymisé en silver)", "Non nul"],
           ["oldbalanceOrg, newbalanceOrig", "décimal", "Solde de l'émetteur avant et après", "Positifs ou nuls"],
           ["nameDest", "texte", "Compte destinataire (pseudonymisé en silver)", "Non nul"],
           ["oldbalanceDest, newbalanceDest", "décimal", "Solde du destinataire avant et après", "Positifs ou nuls"],
           ["isFraud", "booléen", "Étiquette de fraude (vérité terrain)", "0 ou 1. Jamais utilisée comme variable"],
           ["isFlaggedFraud", "booléen", "Signalement par la règle existante", "0 ou 1. Utilisée seulement comme référence de comparaison"]],
          [4.6 * cm, 1.8 * cm, 6.2 * cm, W - 12.6 * cm])]

s += [P("10. Modèle de détection", h1),
      tbl([["Élément", "Décision"],
           ["Cible", "isFraud. Les fraudes n'existent que dans TRANSFER et CASH_OUT : le modèle est appliqué à ces deux types (2 770 409 opérations)."],
           ["Variables", "Montant, type, heure du jour (pas de temps modulo 24), écart de solde de l'émetteur et du destinataire, compte vidé après l'opération, "
            "part du solde déplacée, solde du destinataire nul, nombre et montant des opérations reçues par le destinataire sur 1 h et 24 h."],
           ["Références à battre", "PaySim : règle existante (16 détections), règle « vide le compte » (rappel 97,6 %, précision 0,67 %) et règle « montant égal au solde » (rappel 97,5 %, précision 100 %). Cette dernière est quasi parfaite : le modèle doit l'égaler et compléter les 205 fraudes qu'elle manque. ULB : régression logistique."],
           ["Modèles comparés", "Régression logistique puis LightGBM. Pondération des classes."],
           ["Validation", "Découpage dans le temps sur PaySim : entraînement sur les pas 1 à 323 (4 463 587 opérations, 3 643 fraudes), test sur les pas 324 à 743 (1 899 033 opérations, 4 570 fraudes). Le taux de fraude diffère entre les deux (0,08 % puis 0,24 %) : la dérive est suivie. Aucune variable calculée avec des opérations futures. Validation sur ULB avec découpage temporel sur la variable heure."],
           ["Métriques", "AUC-PR, rappel à taux de fausses alertes fixé (par exemple 0,1 %), nombre d'alertes par heure, coût métier."],
           ["Coût métier", "Fraude non détectée = montant perdu. Fausse alerte = coût fixe de traitement, valeur à calibrer (hypothèse). Le seuil d'alerte minimise le coût total."],
           ["Explication", "SHAP : les trois raisons principales sont renvoyées avec chaque score et stockées dans l'alerte."],
           ["MLOps", "MLflow (expériences, registre), surveillance de la dérive des variables, réentraînement planifié et à la demande."]],
          [3 * cm, W - 3 * cm]),
      P("Limites assumées : PaySim est synthétique et son signal est quasi trivial (une règle de deux conditions détecte 97,5 % des fraudes sans fausse alerte). Un score élevé sur ce jeu "
        "ne prouve pas la performance en conditions réelles. Le jeu S2 est réel mais couvre deux jours et ses variables sont anonymisées. La fraude "
        "est un sujet courant : l'intérêt du projet est le cadre bancaire, l'architecture en flux, l'évaluation par coût et l'explication des alertes.", small)]

s += [P("11. Conformité, sécurité et RGPD", h1)] + B([
    "<b>Données :</b> PaySim est synthétique et S2 est anonymisé. Aucune personne réelle n'est identifiable. La pseudonymisation des comptes est "
    "tout de même mise en œuvre pour démontrer la démarche.",
    "<b>Décision automatisée :</b> le score est une aide. Aucune opération n'est bloquée sans décision d'un analyste. Le RGPD et le cadre DSP2 sont "
    "à vérifier dans les textes officiels avant citation.",
    "<b>Explicabilité :</b> chaque alerte porte ses raisons. Les décisions des analystes sont conservées pour audit.",
    "<b>Minimisation et durées :</b> durées de conservation définies par jeu de données dans le catalogue.",
    "<b>Sécurité :</b> secrets hors du code, aucun fichier de données ni mot de passe dans le dépôt public, réseau Docker interne, journalisation des appels à l'API.",
    "<b>Licences :</b> vérifier les conditions de réutilisation de PaySim et d'ULB avant toute diffusion des données."])

s += [P("12. Planning, recette et risques", h1),
      tbl([["Phase", "Bloc", "Livrables", "Durée estimée"],
           ["1. Cadrage", "BC01", "Besoin, veille, cahier des charges, architecture, RGPD", "2 semaines"],
           ["2. Socle de données", "BC02", "Rejeu Kafka, bronze, silver, qualité, PostgreSQL, MongoDB, catalogue", "4 semaines"],
           ["3. Modèle", "BC02/03", "Variables en flux, entraînement, évaluation par coût, MLflow, SHAP", "3 semaines"],
           ["4. Services et déploiement", "BC03", "API, Airflow, Docker, CI/CD, monitoring, tableau de bord", "3 semaines"],
           ["5. Pilotage et soutenance", "BC04", "Budget et écarts, KPI, formation, mémoire, slides, démo", "2 semaines"]],
          [4 * cm, 1.8 * cm, W - 9.3 * cm, 3.5 * cm]),
      P("Durées indicatives à ajuster à la date de soutenance. Le budget sera chiffré dans le bloc 4.", small),
      P("Critères de recette", h2),
      tbl([["#", "Critère", "Validation"],
           ["R1", "La plateforme démarre avec une commande", "docker compose up"],
           ["R2", "Le rejeu complet produit autant d'événements en bronze qu'en entrée, avec des id_operation uniques", "Comptage : 6 362 620"],
           ["R3", "Un redémarrage d'un service ne crée ni perte ni doublon", "Arrêt puis reprise"],
           ["R4", "Le modèle bat la règle simple à taux de fausses alertes égal", "Rapport MLflow sur le jeu de test"],
           ["R5", "L'API renvoie score et raisons en moins de 100 ms", "Mesure au 95e centile"],
           ["R6", "Le tableau de bord se met à jour pendant le rejeu", "Démonstration en direct"],
           ["R7", "Tests et build passent en CI", "Pipeline GitHub Actions vert"]],
          [1.2 * cm, W - 6.5 * cm, 5.3 * cm]),
      P("Risques", h2),
      tbl([["Risque", "Impact", "Parade"],
           ["Signal trop facile sur PaySim", "Performances surestimées", "Règles de référence mesurées, validation du modèle sur le jeu réel S2, présentation honnête"],
           ["Jeu synthétique, pas de vraie banque", "Crédibilité du cas", "Le dire dans le mémoire, hypothèse de travail assumée"],
           ["Pas d'historique par client", "Variables de fréquence par client inutilisables", "Variables côté destinataire, mesurées avant conception"],
           ["Fausses alertes trop nombreuses", "Charge des analystes", "Seuil choisi par coût, métrique à taux de fausses alertes fixé"],
           ["Charge sur le poste local", "Rejeu lent ou instable", "Vitesse de rejeu réglable, échantillon en développement"],
           ["Téléchargement indisponible", "Pas de données", "Fichiers conservés localement dans data/raw"]],
          [4.4 * cm, 4 * cm, W - 8.4 * cm])]

doc.build(s)
print(OUT)
