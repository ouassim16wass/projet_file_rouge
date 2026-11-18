CREATE SCHEMA IF NOT EXISTS gold;

CREATE TABLE IF NOT EXISTS gold.variables_operation (
    id_operation bigint PRIMARY KEY,
    pas smallint NOT NULL,
    heure_du_jour smallint NOT NULL CHECK (heure_du_jour BETWEEN 0 AND 23),
    jour smallint NOT NULL,
    type text NOT NULL CHECK (type IN ('TRANSFER', 'CASH_OUT')),
    montant numeric(18, 2) NOT NULL CHECK (montant >= 0),
    solde_emetteur_avant numeric(18, 2) NOT NULL,
    solde_emetteur_apres numeric(18, 2) NOT NULL,
    solde_destinataire_avant numeric(18, 2) NOT NULL,
    solde_destinataire_apres numeric(18, 2) NOT NULL,
    type_destinataire text NOT NULL CHECK (type_destinataire IN ('client', 'marchand')),
    ecart_solde_emetteur numeric(18, 2) NOT NULL,
    ecart_solde_destinataire numeric(18, 2) NOT NULL,
    compte_vide_apres boolean NOT NULL,
    montant_egal_solde boolean NOT NULL,
    part_solde_deplacee double precision,
    nb_recus_destinataire_avant integer NOT NULL,
    montant_recu_destinataire_avant numeric(20, 2) NOT NULL,
    destinataire_inconnu boolean NOT NULL,
    jeu_donnees text NOT NULL CHECK (jeu_donnees IN ('apprentissage', 'test')),
    est_fraude smallint NOT NULL CHECK (est_fraude IN (0, 1)),
    controles_qualite text NOT NULL DEFAULT ''
);

CREATE INDEX IF NOT EXISTS idx_variables_pas ON gold.variables_operation (pas);
CREATE INDEX IF NOT EXISTS idx_variables_jeu ON gold.variables_operation (jeu_donnees);

CREATE TABLE IF NOT EXISTS gold.indicateurs_horaires (
    pas smallint NOT NULL,
    type text NOT NULL,
    heure_du_jour smallint NOT NULL,
    nb_operations integer NOT NULL,
    montant_total numeric(20, 2) NOT NULL,
    montant_moyen numeric(18, 2) NOT NULL,
    nb_fraudes integer NOT NULL,
    nb_avertissements integer NOT NULL,
    PRIMARY KEY (pas, type)
);

CREATE TABLE IF NOT EXISTS gold.journal_chargement (
    id bigserial PRIMARY KEY,
    table_cible text NOT NULL,
    lignes_lues bigint NOT NULL,
    lignes_en_base bigint NOT NULL,
    duree_secondes numeric(10, 2) NOT NULL,
    charge_le timestamptz NOT NULL DEFAULT now()
);

CREATE OR REPLACE VIEW gold.taux_fraude_par_type AS
SELECT type,
       count(*) AS nb_operations,
       sum(est_fraude) AS nb_fraudes,
       round(100.0 * sum(est_fraude) / count(*), 4) AS taux_fraude_pct
FROM gold.variables_operation
GROUP BY type;
