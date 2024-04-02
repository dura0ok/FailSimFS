CREATE TABLE IF NOT EXISTS RandomText (
    id SERIAL PRIMARY KEY,
    text_column TEXT
);

-- Generate and insert random text into the table
INSERT INTO RandomText (text_column)
SELECT md5(random()::text)
FROM generate_series(1, 100000) AS gs;