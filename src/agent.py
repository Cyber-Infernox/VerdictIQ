# agent.py
from smolagents import LiteLLMModel, CodeAgent
from tools import fetch_recent_form, fetch_head_to_head

model = LiteLLMModel(
    model_id="ollama_chat/gemma3:4b",
    api_base="http://127.0.0.1:11434",
    num_ctx=8192,
)

agent = CodeAgent(
    tools=[fetch_recent_form, fetch_head_to_head],
    model=model,
)


def predict_with_agent(team1: str, team2: str) -> str:
    """
    Runs the agent to predict the outcome of a match between two teams,
    using whatever data tools it has access to. Returns the agent's
    final answer as a string (winner, confidence, and reasoning).
    """
    task = (
        f"Predict the winner of an upcoming match between '{team1}' and '{team2}'.\n\n"
        f"Steps:\n"
        f"1. Call fetch_recent_form for both teams.\n"
        f"2. Call fetch_head_to_head for the pair.\n"
        f"3. Look closely at 'matches_counted' in both results. This tells you how "
        f"much data you actually have. If matches_counted is 1 or 2, that is a VERY "
        f"small sample — do not describe it as 'strong' or 'excellent' form. Say "
        f"explicitly that the sample size is small and your confidence should be "
        f"moderate (e.g. 50-60%) rather than high, regardless of the result.\n"
        f"4. Only express high confidence (70%+) if matches_counted is 4 or 5 for "
        f"both teams AND the data clearly favors one side.\n\n"
        f"When you are ready to finish, call final_answer with ONE single string "
        f"argument containing your full answer — do not pass separate keyword "
        f"arguments like winner= or confidence=. Format that single string exactly "
        f"like this:\n"
        f"Winner: <team name or 'Too close to call'>\n"
        f"Confidence: <percentage>\n"
        f"Reasoning: <2-3 sentences, explicitly mentioning data sample size>"
    )
    return agent.run(task)