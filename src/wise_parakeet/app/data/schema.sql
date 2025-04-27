CREATE TABLE IF NOT EXISTS models (
    id INTEGER NOT NULL UNIQUE PRIMARY KEY AUTOINCREMENT,
    created_at INTEGER NOT NULL,
    typ TEXT NOT NULL,
    threshold FLOAT NOT NULL,
    pkl_pth TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS vocabs (
    id INTEGER not NULL UNIQUE PRIMARY KEY AUTOINCREMENT,
    created_at INTEGER NOT NULL,
    pkl_pth TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS model_vocabs (
    model_id INTEGER NOT NULL UNIQUE,
    vocab_id INTEGER NOT NULL,
    PRIMARY KEY(model_id, vocab_id),
    FOREIGN KEY(model_id) REFERENCES models(id),
    FOREIGN KEY(vocab_id) REFERENCES vocabs(id)
);

