import sqlite3
import os

DB_PATH = os.environ.get("DATABASE_URL", "verdictiq.db")

_form_cache = {}
_h2h_cache = {}

TEAM_ALIASES = {
    "manchester united": "man united",
    "manchester city": "man city",
    "paris saint-germain": "paris sg",
    "paris saint germain": "paris sg",
    "psg": "paris sg",
    "atletico madrid": "atletico madrid",
    "inter milan": "inter",
    "ac milan": "milan",
    "tottenham": "tottenham",
    "tottenham hotspur": "tottenham",
    "newcastle": "newcastle",
    "newcastle united": "newcastle",
    "wolverhampton": "wolves",
    "wolverhampton wanderers": "wolves",
    "west ham": "west ham",
    "west ham united": "west ham",
    "brighton": "brighton",
    "brighton & hove albion": "brighton",
    "nottingham forest": "nott'm forest",
    "sheffield united": "sheffield united",
    "aston villa": "aston villa",
    "bayer leverkusen": "leverkusen",
    "rb leipzig": "leipzig",
    "borussia dortmund": "dortmund",
    "borussia monchengladbach": "m'gladbach",
}

def _resolve_name(team_name):
    """
    Resolves a user-typed team name to the name stored in the database.
    Falls back to the original name if no alias is found.
    """
    key = team_name.lower().strip()
    return TEAM_ALIASES.get(key, key)

def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_recent_form(team_name, num_matches=5):
    resolved = _resolve_name(team_name)
    cache_key = (resolved, num_matches)

    if cache_key in _form_cache:
        return _form_cache[cache_key]

    conn = _get_conn()

    rows = conn.execute("""
        SELECT date, home_team, away_team, home_score, away_score
        FROM matches
        WHERE home_team = ? OR away_team = ?
        ORDER BY date DESC
        LIMIT ?
    """, (resolved, resolved, num_matches)).fetchall()

    conn.close()

    if not rows:
        print(f"[data_collector] No matches found for '{team_name}' (resolved: '{resolved}')")
        return None

    wins = 0
    draws = 0
    losses = 0
    matches_counted = 0

    for row in rows:
        is_home = row["home_team"] == resolved
        team_score = row["home_score"] if is_home else row["away_score"]
        opp_score = row["away_score"] if is_home else row["home_score"]

        if team_score > opp_score:
            wins += 1
        elif team_score < opp_score:
            losses += 1
        else:
            draws += 1

        matches_counted += 1

    result = {
        "wins": wins,
        "draws": draws,
        "losses": losses,
        "matches_counted": matches_counted,
    }

    _form_cache[cache_key] = result
    return result

def get_head_to_head(team1, team2, num_matches=5):
    resolved1 = _resolve_name(team1)
    resolved2 = _resolve_name(team2)
    cache_key = tuple(sorted([resolved1, resolved2])) + (num_matches,)

    if cache_key in _h2h_cache:
        return _h2h_cache[cache_key]

    empty_result = {
        "team1_wins": 0,
        "team2_wins": 0,
        "draws": 0,
        "matches_counted": 0,
    }

    conn = _get_conn()

    rows = conn.execute("""
        SELECT home_team, away_team, home_score, away_score
        FROM matches
        WHERE (home_team = ? AND away_team = ?)
           OR (home_team = ? AND away_team = ?)
        ORDER BY date DESC
        LIMIT ?
    """, (resolved1, resolved2, resolved2, resolved1, num_matches)).fetchall()

    conn.close()

    if not rows:
        print(f"[data_collector] No H2H history for '{team1}' vs '{team2}'")
        _h2h_cache[cache_key] = empty_result
        return empty_result

    team1_wins = 0
    team2_wins = 0
    draws = 0
    matches_counted = 0

    for row in rows:
        is_team1_home = row["home_team"] == resolved1
        t1_score = row["home_score"] if is_team1_home else row["away_score"]
        t2_score = row["away_score"] if is_team1_home else row["home_score"]

        if t1_score > t2_score:
            team1_wins += 1
        elif t2_score > t1_score:
            team2_wins += 1
        else:
            draws += 1

        matches_counted += 1

    result = {
        "team1_wins": team1_wins,
        "team2_wins": team2_wins,
        "draws": draws,
        "matches_counted": matches_counted,
    }

    _h2h_cache[cache_key] = result
    return result