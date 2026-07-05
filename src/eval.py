from agent import predict_with_agent

test_pairs = [
    ("Argentina", "Brazil"),
    ("Real Madrid", "Barcelona"),
    ("Manchester United", "Liverpool"),
    ("France", "Germany"),
]

for team1, team2 in test_pairs:
    print(f"\n{'='*60}")
    print(f"MATCH: {team1} vs {team2}")
    print('='*60)
    result = predict_with_agent(team1, team2)
    print(result)