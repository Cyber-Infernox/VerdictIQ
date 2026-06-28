import requests
from datetime import datetime

BASE_URL = "https://www.thesportsdb.com/api/v1/json/123"

# Simple in-memory cache so repeated predictions for the same team
# don't re-hit the API every time during testing/dev.
_team_id_cache = {}
_form_cache = {}
_h2h_cache = {}

def get_team_id(team_name):
    key = team_name.lower().strip()

    if key in _team_id_cache:
        return _team_id_cache[key]

    url = f"{BASE_URL}/searchteams.php?t={team_name}"

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"[data_collector] Error fetching team ID for '{team_name}': {e}")
        return None

    data = response.json()
    teams = data.get("teams")

    if not teams:
        print(f"[data_collector] No team found for '{team_name}'")
        return None

    exact_match = next(
        (t for t in teams if t["strTeam"].lower() == key),
        None
    )
    chosen = exact_match or teams[0]

    if not exact_match and len(teams) > 1:
        print(
            f"[data_collector] Ambiguous match for '{team_name}', "
            f"defaulting to '{chosen['strTeam']}'. "
            f"Other matches: {[t['strTeam'] for t in teams]}"
        )

    result = {
        "id": chosen["idTeam"],
        "official_name": chosen["strTeam"],
    }
    _team_id_cache[key] = result
    return result

def get_recent_form(team_name, num_matches=5):
    key = team_name.lower().strip()
    cache_key = (key, num_matches)

    if cache_key in _form_cache:
        return _form_cache[cache_key]

    team_info = get_team_id(team_name)

    if not team_info:
        return None

    team_id = team_info["id"]
    official_name = team_info["official_name"]  # use this for matching, not raw input

    url = f"{BASE_URL}/eventslast.php?id={team_id}"

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"[data_collector] Error fetching recent form for '{team_name}': {e}")
        return None

    data = response.json()
    events = data.get("results") or []

    if not events:
        print(f"[data_collector] No recent match data for '{team_name}'")
        return None

    def match_date(match):
        date_str = match.get("dateEvent", "")
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except (ValueError, TypeError):
            return datetime.min

    events = sorted(events, key=match_date, reverse=True)

    wins = 0
    draws = 0
    losses = 0
    matches_counted = 0

    for match in events:
        home = match.get("strHomeTeam")
        away = match.get("strAwayTeam")
        home_score_raw = match.get("intHomeScore")
        away_score_raw = match.get("intAwayScore")

        if home_score_raw is None or away_score_raw is None:
            continue

        try:
            home_score = int(home_score_raw)
            away_score = int(away_score_raw)
        except (TypeError, ValueError):
            continue

        # Compare against the resolved official name, not the raw user input
        if official_name.lower() == (home or "").lower():
            team_score, opponent_score = home_score, away_score
        elif official_name.lower() == (away or "").lower():
            team_score, opponent_score = away_score, home_score
        else:
            continue

        if team_score > opponent_score:
            wins += 1
        elif team_score < opponent_score:
            losses += 1
        else:
            draws += 1

        matches_counted += 1

        if matches_counted >= num_matches:
            break

    if matches_counted == 0:
        print(f"[data_collector] No valid completed matches found for '{team_name}'")
        return None

    result = {
        "wins": wins,
        "draws": draws,
        "losses": losses,
        "matches_counted": matches_counted,
    }

    _form_cache[cache_key] = result
    return result
    key = team_name.lower().strip()

    if key in _form_cache:
        return _form_cache[key]

    team_id = get_team_id(team_name)

    if not team_id:
        return None

    url = f"{BASE_URL}/eventslast.php?id={team_id}"

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"[data_collector] Error fetching recent form for '{team_name}': {e}")
        return None

    data = response.json()
    events = data.get("results") or []

    if not events:
        print(f"[data_collector] No recent match data for '{team_name}'")
        return None

    # Don't trust the API's default ordering — sort explicitly by date,
    # most recent first.
    def match_date(match):
        date_str = match.get("dateEvent", "")
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except (ValueError, TypeError):
            return datetime.min

    events = sorted(events, key=match_date, reverse=True)

    wins = 0
    draws = 0
    losses = 0
    matches_counted = 0

    for match in events:
        home = match.get("strHomeTeam")
        away = match.get("strAwayTeam")
        home_score_raw = match.get("intHomeScore")
        away_score_raw = match.get("intAwayScore")

        # Skip matches with missing/unplayed scores (e.g. postponed, future fixtures)
        if home_score_raw is None or away_score_raw is None:
            continue

        try:
            home_score = int(home_score_raw)
            away_score = int(away_score_raw)
        except (TypeError, ValueError):
            continue

        if team_name.lower() == (home or "").lower():
            team_score, opponent_score = home_score, away_score
        elif team_name.lower() == (away or "").lower():
            team_score, opponent_score = away_score, home_score
        else:
            # Shouldn't normally happen, but guard against mismatched data
            continue

        if team_score > opponent_score:
            wins += 1
        elif team_score < opponent_score:
            losses += 1
        else:
            draws += 1

        matches_counted += 1

        if matches_counted >= num_matches:
            break

    if matches_counted == 0:
        print(f"[data_collector] No valid completed matches found for '{team_name}'")
        return None

    result = {
        "wins": wins,
        "draws": draws,
        "losses": losses,
        "matches_counted": matches_counted,
    }

    _form_cache[key] = result
    return result

def get_head_to_head(team1, team2):
    """
    Searches for past meetings between two teams using TheSportsDB's
    searchevents.php endpoint. Tries both name orderings since we don't
    know which team was historically 'home'.

    NOTE: On the free tier, this endpoint is limited to 1 result per
    request, so results will often be sparse — sometimes just one
    match, sometimes none at all. This is an API limitation, not a bug.
    """
    cache_key = tuple(sorted([team1.lower().strip(), team2.lower().strip()]))

    if cache_key in _h2h_cache:
        return _h2h_cache[cache_key]

    def search_event_name(name_combo):
        url = f"{BASE_URL}/searchevents.php?e={name_combo}"
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"[data_collector] Error searching '{name_combo}': {e}")
            return []

        data = response.json()
        return data.get("event") or []

    combo_a = f"{team1.replace(' ', '_')}_vs_{team2.replace(' ', '_')}"
    combo_b = f"{team2.replace(' ', '_')}_vs_{team1.replace(' ', '_')}"

    events = search_event_name(combo_a) + search_event_name(combo_b)

    if not events:
        print(f"[data_collector] No head-to-head history found for '{team1}' vs '{team2}'")
        result = {
            "team1_wins": 0,
            "team2_wins": 0,
            "draws": 0,
            "matches_counted": 0,
        }
        _h2h_cache[cache_key] = result
        return result

    team1_wins = 0
    team2_wins = 0
    draws = 0
    matches_counted = 0

    for match in events:
        home = match.get("strHomeTeam")
        away = match.get("strAwayTeam")
        home_score_raw = match.get("intHomeScore")
        away_score_raw = match.get("intAwayScore")

        if home_score_raw is None or away_score_raw is None:
            continue

        try:
            home_score = int(home_score_raw)
            away_score = int(away_score_raw)
        except (TypeError, ValueError):
            continue

        if team1.lower() == (home or "").lower():
            t1_score, t2_score = home_score, away_score
        elif team1.lower() == (away or "").lower():
            t1_score, t2_score = away_score, home_score
        else:
            continue

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