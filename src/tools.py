from smolagents import tool
from predictor import predict
from data_collector import get_recent_form, get_head_to_head

@tool
def fetch_recent_form(team_name: str) -> dict:
    """
    Fetches a team's recent match form (wins, draws, losses) based on
    their last 5 completed matches from the database.

    Args:
        team_name: The name of the team to look up.

    Returns:
        A dictionary with keys: wins, draws, losses, matches_counted.
        If the team is not found in the database, returns a dictionary
        with an 'error' key explaining the team was not found — do NOT
        invent or assume form data in this case.
    """
    result = get_recent_form(team_name)
    if result is None:
        return {
            "error": f"No data found for '{team_name}' in the database. "
                     f"This team may be a club team — the current database "
                     f"only contains international (national team) matches."
        }
    return result

@tool
def fetch_head_to_head(team1: str, team2: str) -> dict:
    """
    Fetches historical head-to-head results between two specific teams.

    Args:
        team1: First team's name.
        team2: Second team's name.

    Returns:
        A dictionary with keys: team1_wins, team2_wins, draws, matches_counted.
        If no history is found, matches_counted will be 0 — do NOT invent
        or assume head-to-head data.
    """
    return get_head_to_head(team1, team2)

@tool
def predict_match(team1: str, team2: str) -> dict:
    """
    Predicts the winner between two teams using recent form,
    head-to-head history, and a deterministic scoring engine.

    Args:
        team1: Name of the first team participating in the match.
        team2: Name of the second team participating in the match.

    Returns:
        A dictionary containing the predicted winner, confidence percentage,
        team statistics, form scores, final scores, head-to-head data,
        and prediction weights.
    """
    return predict(team1, team2, verbose=True)