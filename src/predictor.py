from data_collector import get_recent_form, get_head_to_head

FORM_WEIGHT = 0.65
H2H_WEIGHT = 0.35

def calculate_form_score(form):
    """
    Returns a normalized form score between 0 and 1.
    """
    matches = form.get("matches_counted", 0)

    if matches == 0:
        return 0

    raw_score = form["wins"] * 3 + form["draws"]
    max_possible = matches * 3

    return raw_score / max_possible

def calculate_h2h_scores(h2h):
    """
    Returns normalized head-to-head scores.
    """
    matches = h2h.get("matches_counted", 0)

    if matches == 0:
        return None, None

    max_possible = matches * 3

    team1_raw = h2h["team1_wins"] * 3 + h2h["draws"]
    team2_raw = h2h["team2_wins"] * 3 + h2h["draws"]

    return team1_raw / max_possible, team2_raw / max_possible

def predict(team1, team2, verbose=True):

    if verbose:
        print("\n========== FETCHING FORM DATA ==========")

    form1 = get_recent_form(team1)
    form2 = get_recent_form(team2)

    if not form1 or not form2:
        missing = []

        if not form1:
            missing.append(team1)

        if not form2:
            missing.append(team2)

        if verbose:
            print(f"\n[predictor] Could not fetch data for: {', '.join(missing)}")

        return {
            "winner": "Unable to Predict",
            "confidence": 0,
            "team1": None,
            "team2": None,
            "head_to_head": None,
        }

    if verbose:
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

    if verbose:
        print("\n========== FETCHING HEAD-TO-HEAD DATA ==========")

    h2h = get_head_to_head(team1, team2)

    if verbose:
        print(f"Matches found: {h2h['matches_counted']}")

        if h2h["matches_counted"] > 0:
            print(f"{team1} Wins : {h2h['team1_wins']}")
            print(f"{team2} Wins : {h2h['team2_wins']}")
            print(f"Draws        : {h2h['draws']}")
        else:
            print("No head-to-head history available — relying on form only.")

    h2h_score1, h2h_score2 = calculate_h2h_scores(h2h)

    if verbose:
        print("\n========== CALCULATING FINAL SCORES ==========")

    if h2h_score1 is not None:
        final_score1 = (FORM_WEIGHT * form_score1) + (H2H_WEIGHT * h2h_score1)
        final_score2 = (FORM_WEIGHT * form_score2) + (H2H_WEIGHT * h2h_score2)

        if verbose:
            print(
                f"{team1}: Form={round(form_score1,3)} "
                f"H2H={round(h2h_score1,3)} "
                f"Final={round(final_score1,3)}"
            )

            print(
                f"{team2}: Form={round(form_score2,3)} "
                f"H2H={round(h2h_score2,3)} "
                f"Final={round(final_score2,3)}"
            )

    else:
        final_score1 = form_score1
        final_score2 = form_score2

        if verbose:
            print(
                f"{team1}: Form={round(form_score1,3)} "
                f"(H2H unavailable) "
                f"Final={round(final_score1,3)}"
            )

            print(
                f"{team2}: Form={round(form_score2,3)} "
                f"(H2H unavailable) "
                f"Final={round(final_score2,3)}"
            )

    total = final_score1 + final_score2

    if total == 0:
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

    if verbose:
        print("\n========== FINAL RESULT ==========")
        print(f"Winner     : {winner}")
        print(f"Confidence : {confidence}%")

    return {
        "winner": winner,
        "confidence": confidence,

        "team1": {
            "name": team1,
            "form": form1,
            "form_score": round(form_score1, 3),
            "final_score": round(final_score1, 3),
        },

        "team2": {
            "name": team2,
            "form": form2,
            "form_score": round(form_score2, 3),
            "final_score": round(final_score2, 3),
        },

        "head_to_head": h2h,

        "weights": {
            "form": FORM_WEIGHT,
            "head_to_head": H2H_WEIGHT,
        },
    }