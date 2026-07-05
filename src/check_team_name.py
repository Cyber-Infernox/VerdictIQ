import sqlite3

def find_team(search_term):
    conn = sqlite3.connect("verdictiq.db")
    rows = conn.execute("""
        SELECT DISTINCT home_team FROM matches
        WHERE home_team LIKE ?
        ORDER BY home_team
    """, (f"%{search_term.lower()}%",)).fetchall()
    conn.close()
    return [row[0] for row in rows]

term = input("Search team name: ").strip()
results = find_team(term)
if results:
    print(f"\nFound {len(results)} matches:")
    for r in results:
        print(f"  {r}")
else:
    print("No matches found.")