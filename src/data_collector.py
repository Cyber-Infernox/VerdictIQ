# data_collector.py
import os
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://v3.football.api-sports.io"
API_KEY = os.environ.get("API_FOOTBALL_KEY")

HEADERS = {
    "x-apisports-key": API_KEY,
}

# API-Football's "season" parameter wants a starting year, e.g. 2025 for
# the 2025/26 season. We default to the current year and let the season
# logic below handle the year-boundary case for leagues that start mid-year.
CURRENT_YEAR = datetime.now().year

_team_id_cache = {}
_form_cache = {}
_h2h_cache = {}


def _check_api_errors(data, context=""):
    errors = data.get("errors")
    if errors:
        print(f"[data_collector] API error{f' ({context})' if context else ''}: {errors}")
        return True
    return False


def get_team_id(team_name):
    key = team_name.lower().strip()

    if key in _team_id_cache:
        return _team_id_cache[key]

    if not API_KEY:
        print("[data_collector] No API_FOOTBALL_KEY set. Check your .env file.")
        return None

    url = f"{BASE_URL}/teams"
    params = {"search": team_name}

    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=5)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"[data_collector] Error fetching team ID for '{team_name}': {e}")
        return None

    data = response.json()

    if _check_api_errors(data, context=f"searching '{team_name}'"):
        return None

    results = data.get("response") or []

    if not results:
        print(f"[data_collector] No team found for '{team_name}'")
        return None

    exact_match = next(
        (r for r in results if r["team"]["name"].lower() == key),
        None
    )
    chosen = exact_match or results[0]

    if not exact_match and len(results) > 1:
        print(
            f"[data_collector] Ambiguous match for '{team_name}', "
            f"defaulting to '{chosen['team']['name']}'. "
            f"Other matches: {[r['team']['name'] for r in results]}"
        )

    result = {
        "id": chosen["team"]["id"],
        "official_name": chosen["team"]["name"],
    }
    _team_id_cache[key] = result
    return result


def _parse_fixture_date(fixture):
    date_str = fixture.get("fixture", {}).get("date", "")
    try:
        return datetime.fromisoformat(date_str)
    except (ValueError, TypeError):
        return datetime.min.replace(tzinfo=timezone.utc)


def _fetch_team_fixtures(team_id, season):
    """
    Fetches ALL fixtures for a team in a given season (free tier doesn't
    support the 'last' parameter, so we pull everything and filter/sort
    ourselves).
    """
    url = f"{BASE_URL}/fixtures"
    params = {"team": team_id, "season": season}

    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"[data_collector] Error fetching fixtures (team={team_id}, season={season}): {e}")
        return None

    data = response.json()

    if _check_api_errors(data, context=f"fetching fixtures for team {team_id}"):
        return None

    return data.get("response") or []


def get_recent_form(team_name, num_matches=5, season=None):
    season = season or CURRENT_YEAR
    key = team_name.lower().strip()
    cache_key = (key, num_matches, season)

    if cache_key in _form_cache:
        return _form_cache[cache_key]

    team_info = get_team_id(team_name)

    if not team_info:
        return None

    team_id = team_info["id"]

    fixtures = _fetch_team_fixtures(team_id, season)

    if fixtures is None:
        return None

    if not fixtures:
        print(f"[data_collector] No fixtures found for '{team_name}' in season {season}")
        return None

    # Only keep finished matches, then sort most-recent-first
    finished = [
        f for f in fixtures
        if f.get("fixture", {}).get("status", {}).get("short") in ("FT", "AET", "PEN")
    ]
    finished.sort(key=_parse_fixture_date, reverse=True)

    recent = finished[:num_matches]

    wins = 0
    draws = 0
    losses = 0
    matches_counted = 0

    for match in recent:
        home_team = match.get("teams", {}).get("home", {})
        away_team = match.get("teams", {}).get("away", {})

        is_home = home_team.get("id") == team_id
        team_side = home_team if is_home else away_team

        winner_flag = team_side.get("winner")

        if winner_flag is True:
            wins += 1
        elif winner_flag is False:
            losses += 1
        else:
            draws += 1

        matches_counted += 1

    if matches_counted == 0:
        print(f"[data_collector] No completed matches found for '{team_name}' in season {season}")
        return None

    result = {
        "wins": wins,
        "draws": draws,
        "losses": losses,
        "matches_counted": matches_counted,
    }

    _form_cache[cache_key] = result
    return result


def get_head_to_head(team1, team2, num_matches=5):
    cache_key = tuple(sorted([team1.lower().strip(), team2.lower().strip()])) + (num_matches,)

    if cache_key in _h2h_cache:
        return _h2h_cache[cache_key]

    team1_info = get_team_id(team1)
    team2_info = get_team_id(team2)

    empty_result = {
        "team1_wins": 0,
        "team2_wins": 0,
        "draws": 0,
        "matches_counted": 0,
    }

    if not team1_info or not team2_info:
        _h2h_cache[cache_key] = empty_result
        return empty_result

    team1_id = team1_info["id"]
    team2_id = team2_info["id"]

    url = f"{BASE_URL}/fixtures/headtohead"
    params = {"h2h": f"{team1_id}-{team2_id}"}

    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"[data_collector] Error fetching head-to-head for '{team1}' vs '{team2}': {e}")
        return None

    data = response.json()

    if _check_api_errors(data, context=f"fetching H2H for '{team1}' vs '{team2}'"):
        return None

    fixtures = data.get("response") or []

    finished = [
        f for f in fixtures
        if f.get("fixture", {}).get("status", {}).get("short") in ("FT", "AET", "PEN")
    ]
    finished.sort(key=_parse_fixture_date, reverse=True)

    recent = finished[:num_matches]

    if not recent:
        print(f"[data_collector] No head-to-head history found for '{team1}' vs '{team2}'")
        _h2h_cache[cache_key] = empty_result
        return empty_result

    team1_wins = 0
    team2_wins = 0
    draws = 0
    matches_counted = 0

    for match in recent:
        home_team = match.get("teams", {}).get("home", {})
        away_team = match.get("teams", {}).get("away", {})

        if home_team.get("id") == team1_id:
            team1_side = home_team
        elif away_team.get("id") == team1_id:
            team1_side = away_team
        else:
            continue

        winner_flag = team1_side.get("winner")

        if winner_flag is True:
            team1_wins += 1
        elif winner_flag is False:
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