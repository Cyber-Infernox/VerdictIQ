from agent import predict_with_agent

team1 = input("Team 1: ").strip()
team2 = input("Team 2: ").strip()

if not team1 or not team2:
    print("\nPlease enter both team names.")
else:
    result = predict_with_agent(team1, team2)
    print("\n" + result)