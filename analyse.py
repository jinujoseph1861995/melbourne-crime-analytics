import pandas as pd
import psycopg2

conn = psycopg2.connect(
    host     = "localhost",
    port     = 5432,
    dbname   = "melbourne_crime",
    user     = "postgres",
    password = "password"
)

# Finding 1 — Top 10 LGAs by crime (most recent year)
top_lgas = pd.read_sql("""
    SELECT
        lga,
        SUM(incidents)               AS total_incidents,
        ROUND(AVG(rate_per_100k), 1) AS rate_per_100k
    FROM crime_incidents
    WHERE year = (SELECT MAX(year) FROM crime_incidents)
    GROUP BY lga
    ORDER BY total_incidents DESC
    LIMIT 10
""", conn)

# Finding 2 — Is crime going up or down overall?
yearly_trend = pd.read_sql("""
    SELECT
        year,
        SUM(incidents) AS total_incidents
    FROM crime_incidents
    GROUP BY year
    ORDER BY year
""", conn)

# Finding 3 — What types of crime happen most?
by_type = pd.read_sql("""
    SELECT
        offence_division,
        SUM(incidents) AS total_incidents
    FROM crime_incidents
    WHERE year = (SELECT MAX(year) FROM crime_incidents)
    GROUP BY offence_division
    ORDER BY total_incidents DESC
""", conn)

# Finding 4 — Which LGA improved the most?
lga_change = pd.read_sql("""
    SELECT
        lga,
        SUM(CASE WHEN year = (SELECT MAX(year) FROM crime_incidents)
                 THEN incidents END) AS latest_year,
        SUM(CASE WHEN year = (SELECT MIN(year) FROM crime_incidents)
                 THEN incidents END) AS first_year,
        SUM(CASE WHEN year = (SELECT MAX(year) FROM crime_incidents)
                 THEN incidents END) -
        SUM(CASE WHEN year = (SELECT MIN(year) FROM crime_incidents)
                 THEN incidents END) AS total_change
    FROM crime_incidents
    GROUP BY lga
    ORDER BY total_change
""", conn)

conn.close()

print("\n" + "="*55)
print("  TOP 10 LGAs BY CRIME — LATEST YEAR")
print("="*55)
print(top_lgas.to_string(index=False))

print("\n" + "="*55)
print("  TOTAL CRIME BY YEAR")
print("="*55)
print(yearly_trend.to_string(index=False))

print("\n" + "="*55)
print("  CRIME BY TYPE — LATEST YEAR")
print("="*55)
print(by_type.to_string(index=False))

print("\n" + "="*55)
print("  LGA IMPROVEMENT OVER TIME")
print("="*55)
print(lga_change.to_string(index=False))

print("\n✓ Copy these numbers into your README!")