# tools.py
from smolagents import tool
from data_collector import get_recent_form, get_head_to_head


@tool
def fetch_recent_form(team_name: str) -> dict:
    """
    Fetches a team's recent match form (wins, draws, losses) based on
    their last 5 completed matches.

    Args:
        team_name: The name of the team to look up.

    Returns:
        A dictionary with keys: wins, draws, losses, matches_counted.
        Returns None if the team can't be found or has no recent match data.
    """
    return get_recent_form(team_name)


@tool
def fetch_head_to_head(team1: str, team2: str) -> dict:
    """
    Fetches historical head-to-head results between two specific teams.

    Args:
        team1: First team's name.
        team2: Second team's name.

    Returns:
        A dictionary with keys: team1_wins, team2_wins, draws, matches_counted.
        matches_counted will often be 0 or very low — this data source has
        limited historical coverage, so treat low counts as 'not much
        reliable signal here' rather than as evidence of an even matchup.
    """
    return get_head_to_head(team1, team2)