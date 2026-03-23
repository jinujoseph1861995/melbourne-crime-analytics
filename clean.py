import pandas as pd
import os

INPUT_FILE  = "data/raw/crime_data.xlsx"
OUTPUT_FILE = "data/processed/crime_clean.csv"

os.makedirs("data/processed", exist_ok=True)

print("Reading Excel file...")

# ── Find the header row automatically ────────────────────
df_raw = pd.read_excel(
    INPUT_FILE,
    sheet_name="Table 02",
    engine="calamine",
    header=None
)

header_row = None
for i, row in df_raw.iterrows():
    if str(row[0]).strip().lower() == "year":
        header_row = i
        break

print(f"Header found at row: {header_row}")

# ── Read the real data ────────────────────────────────────
df = pd.read_excel(
    INPUT_FILE,
    sheet_name="Table 02",
    engine="calamine",
    skiprows=header_row,
    header=0
)

# ── Rename columns to clean names ─────────────────────────
df.columns = [
    "year",
    "year_ending",
    "police_service_area",
    "lga",
    "offence_division",
    "offence_subdivision",
    "offence_subgroup",
    "incidents",
    "psa_rate_per_100k",
    "lga_rate_per_100k"
]

# ── Keep only what we need ────────────────────────────────
df = df[[
    "year",
    "lga",
    "offence_division",
    "offence_subdivision",
    "incidents",
    "lga_rate_per_100k"
]]

# ── Rename rate column to match the rest of our project ───
df = df.rename(columns={"lga_rate_per_100k": "rate_per_100k"})

# ── Remove blank rows ─────────────────────────────────────
df = df.dropna(subset=["lga", "incidents"])

# ── Fix data types ────────────────────────────────────────
df["year"]          = pd.to_numeric(df["year"],          errors="coerce")
df["incidents"]     = pd.to_numeric(df["incidents"],     errors="coerce").fillna(0).astype(int)
df["rate_per_100k"] = pd.to_numeric(df["rate_per_100k"], errors="coerce").fillna(0)
df["lga"]           = df["lga"].str.strip().str.title()

# ── Remove rows where year is blank ──────────────────────
df = df.dropna(subset=["year"])
df["year"] = df["year"].astype(int)

# ── Show LGA names so we can verify ──────────────────────
print(f"\nTotal rows before LGA filter: {len(df):,}")
print("\nAll LGA names in your file:")
for lga in sorted(df["lga"].unique()):
    print(f"  '{lga}'")

# ── Filter to Melbourne metro ─────────────────────────────
MELBOURNE_LGAS = {
    "Melbourne", "Yarra", "Port Phillip", "Stonnington",
    "Boroondara", "Bayside", "Darebin", "Moreland",
    "Moonee Valley", "Maribyrnong", "Hobsons Bay",
    "Wyndham", "Casey", "Knox", "Whitehorse"
}

df = df[df["lga"].isin(MELBOURNE_LGAS)]

# ── Save ──────────────────────────────────────────────────
df.to_csv(OUTPUT_FILE, index=False)

print(f"\nClean rows saved: {len(df):,}")
print(f"Saved to: {OUTPUT_FILE}")
print("Done! Now run: python load.py")