from predictor import predict

team1 = input("Team 1: ").strip()
team2 = input("Team 2: ").strip()

if not team1 or not team2:
    print("\nPlease enter both team names.")
else:
    result = predict(team1, team2)

    print()
    print(f"Prediction: {result['winner']}")
    print(f"Confidence: {result['confidence']}%")