from data_collector import get_recent_form, get_head_to_head

# Weight given to recent form vs head-to-head when H2H data is available.
FORM_WEIGHT = 0.65
H2H_WEIGHT = 0.35


def calculate_form_score(form):
    """
    Returns a normalized form score between 0 and 1,
    so teams with fewer counted matches aren't unfairly
    over/under-weighted compared to teams with a full sample.
    """
    matches = form.get("matches_counted", 0)

    if matches == 0:
        return 0

    raw_score = form["wins"] * 3 + form["draws"]
    max_possible = matches * 3  # if team won every counted match

    return raw_score / max_possible


def calculate_h2h_scores(h2h):
    """
    Returns (team1_score, team2_score) as normalized 0-1 values based on
    head-to-head history. Returns (None, None) if there's no usable
    head-to-head data — callers should treat this as 'skip this signal',
    not as 'teams are evenly matched'.
    """
    matches = h2h.get("matches_counted", 0)

    if matches == 0:
        return None, None

    max_possible = matches * 3

    team1_raw = h2h["team1_wins"] * 3 + h2h["draws"]
    team2_raw = h2h["team2_wins"] * 3 + h2h["draws"]

    return team1_raw / max_possible, team2_raw / max_possible


def predict(team1, team2):

    print("\n========== FETCHING FORM DATA ==========")

    form1 = get_recent_form(team1)
    form2 = get_recent_form(team2)

    if not form1 or not form2:
        missing = []
        if not form1:
            missing.append(team1)
        if not form2:
            missing.append(team2)

        print(f"\n[predictor] Could not fetch data for: {', '.join(missing)}")

        return {
            "winner": "Unable to Predict",
            "confidence": 0
        }

    print(f"\n{team1} Form (last {form1['matches_counted']} matches):")
    print(f"Wins   : {form1['wins']}")
    print(f"Draws  : {form1['draws']}")
    print(f"Losses : {form1['losses']}")

    print(f"\n{team2} Form (last {form2['matches_counted']} matches):")
    print(f"Wins   : {form2['wins']}")
    print(f"Draws  : {form2['draws']}")
    print(f"Losses : {form2['losses']}")

    form_score1 = calculate_form_score(form1)
    form_score2 = calculate_form_score(form2)

    print("\n========== FETCHING HEAD-TO-HEAD DATA ==========")

    h2h = get_head_to_head(team1, team2)

    print(f"Matches found: {h2h['matches_counted']}")
    if h2h["matches_counted"] > 0:
        print(f"{team1} Wins : {h2h['team1_wins']}")
        print(f"{team2} Wins : {h2h['team2_wins']}")
        print(f"Draws      : {h2h['draws']}")
    else:
        print("No head-to-head history available — relying on form only.")

    h2h_score1, h2h_score2 = calculate_h2h_scores(h2h)

    print("\n========== CALCULATING FINAL SCORES ==========")

    if h2h_score1 is not None:
        # Combine form + head-to-head using weighted average
        final_score1 = (FORM_WEIGHT * form_score1) + (H2H_WEIGHT * h2h_score1)
        final_score2 = (FORM_WEIGHT * form_score2) + (H2H_WEIGHT * h2h_score2)
        print(f"{team1}: Form={round(form_score1, 3)}  H2H={round(h2h_score1, 3)}  Final={round(final_score1, 3)}")
        print(f"{team2}: Form={round(form_score2, 3)}  H2H={round(h2h_score2, 3)}  Final={round(final_score2, 3)}")
    else:
        # No head-to-head data — fall back to form only
        final_score1 = form_score1
        final_score2 = form_score2
        print(f"{team1}: Form={round(form_score1, 3)} (H2H unavailable)  Final={round(final_score1, 3)}")
        print(f"{team2}: Form={round(form_score2, 3)} (H2H unavailable)  Final={round(final_score2, 3)}")

    total = final_score1 + final_score2

    if total == 0:
        # Both teams have no positive signal at all — genuinely no edge
        winner = "Draw"
        confidence = 50
    elif final_score1 > final_score2:
        winner = team1
        confidence = round((final_score1 / total) * 100)
    elif final_score2 > final_score1:
        winner = team2
        confidence = round((final_score2 / total) * 100)
    else:
        winner = "Draw"
        confidence = 50

    print("\n========== FINAL RESULT ==========")
    print(f"Winner     : {winner}")
    print(f"Confidence : {confidence}%")

    return {
        "winner": winner,
        "confidence": confidence
    }