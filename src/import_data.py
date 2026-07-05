import sqlite3
import pandas as pd

DB_PATH = "verdictiq.db"

def create_tables(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS matches (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            date        TEXT NOT NULL,
            home_team   TEXT NOT NULL,
            away_team   TEXT NOT NULL,
            home_score  INTEGER NOT NULL,
            away_score  INTEGER NOT NULL,
            tournament  TEXT,
            match_type  TEXT NOT NULL
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_home_team ON matches(home_team)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_away_team ON matches(away_team)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_date ON matches(date)")
    conn.commit()

def clear_table(conn):
    """Clear existing data before re-importing to avoid duplicates."""
    conn.execute("DELETE FROM matches")
    conn.commit()
    print("Cleared existing match data.")

def import_international(conn, csv_path="results.csv"):
    print(f"\nImporting international matches from '{csv_path}'...")

    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"[import] File not found: '{csv_path}' — skipping.")
        return

    df = df.dropna(subset=["home_score", "away_score"])
    df["home_score"] = df["home_score"].astype(int)
    df["away_score"] = df["away_score"].astype(int)

    df["home_team"] = df["home_team"].str.lower().str.strip()
    df["away_team"] = df["away_team"].str.lower().str.strip()
    df["match_type"] = "international"

    if "tournament" not in df.columns:
        df["tournament"] = ""

    records = df[[
        "date", "home_team", "away_team",
        "home_score", "away_score",
        "tournament", "match_type"
    ]].values.tolist()

    conn.executemany("""
        INSERT INTO matches (date, home_team, away_team, home_score, away_score, tournament, match_type)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, records)
    conn.commit()
    print(f"Imported {len(records)} international matches.")

def import_club(conn, csv_path="Matches.csv"):
    print(f"\nImporting club matches from '{csv_path}'...")

    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"[import] File not found: '{csv_path}' — skipping.")
        return

    df = df.dropna(subset=["FTHome", "FTAway"])
    df["FTHome"] = df["FTHome"].astype(int)
    df["FTAway"] = df["FTAway"].astype(int)

    df["HomeTeam"] = df["HomeTeam"].str.lower().str.strip()
    df["AwayTeam"] = df["AwayTeam"].str.lower().str.strip()
    df["match_type"] = "club"

    records = []
    for _, row in df.iterrows():
        records.append((
            str(row["MatchDate"]),
            row["HomeTeam"],
            row["AwayTeam"],
            int(row["FTHome"]),
            int(row["FTAway"]),
            str(row.get("Division", "")),
            "club",
        ))

    conn.executemany("""
        INSERT INTO matches (date, home_team, away_team, home_score, away_score, tournament, match_type)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, records)
    conn.commit()
    print(f"Imported {len(records)} club matches.")

if __name__ == "__main__":
    conn = sqlite3.connect(DB_PATH)
    create_tables(conn)
    clear_table(conn)
    import_international(conn, "results.csv")
    import_club(conn, "Matches.csv")
    conn.close()

    print("\nDone. Database ready.")