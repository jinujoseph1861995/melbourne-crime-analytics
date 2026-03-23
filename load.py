import pandas as pd
import psycopg2

# ── Connect ───────────────────────────────────────────────
print("Connecting to PostgreSQL...")

conn = psycopg2.connect(
    host     = "localhost",
    port     = 5432,
    dbname   = "melbourne_crime",
    user     = "postgres",
    password = "password"
)
cursor = conn.cursor()
print("Connected! ✓")

# ── Create table ──────────────────────────────────────────
print("Creating table...")

cursor.execute("DROP TABLE IF EXISTS crime_incidents CASCADE;")

cursor.execute("""
    CREATE TABLE crime_incidents (
        id                  SERIAL PRIMARY KEY,
        year                INT,
        lga                 TEXT,
        offence_division    TEXT,
        offence_subdivision TEXT,
        incidents           INT,
        rate_per_100k       NUMERIC(8, 1)
    );
""")
print("Table created! ✓")

# ── Read CSV ──────────────────────────────────────────────
print("Reading clean CSV...")
df = pd.read_csv("data/processed/crime_clean.csv")
print(f"  {len(df):,} rows ready to insert")

# ── Insert rows ───────────────────────────────────────────
print("Loading rows into PostgreSQL...")

rows = [
    tuple(row)
    for row in df[[
        "year",
        "lga",
        "offence_division",
        "offence_subdivision",
        "incidents",
        "rate_per_100k"
    ]].itertuples(index=False, name=None)
]

cursor.executemany("""
    INSERT INTO crime_incidents
        (year, lga, offence_division,
         offence_subdivision, incidents, rate_per_100k)
    VALUES
        (%s, %s, %s, %s, %s, %s)
""", rows)

# ── Save ──────────────────────────────────────────────────
conn.commit()
cursor.close()
conn.close()

print(f"  {len(rows):,} rows loaded ✓")
print("Done! Now run the SQL in pgAdmin.")