DROP TABLE IF EXISTS livres;

CREATE TABLE livres (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titre TEXT NOT NULL,
    auteur TEXT NOT NULL,
    statut INTEGER DEFAULT 0 -- 0 = Dispo, 1 = Emprunté
);
