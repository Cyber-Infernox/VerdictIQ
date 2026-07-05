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
    task = (
        f"Predict the winner of an upcoming match between '{team1}' and '{team2}'.\n\n"
        f"Steps:\n"
        f"1. Call fetch_recent_form for both teams.\n"
        f"2. Call fetch_head_to_head for the pair.\n"
        f"3. If either team returns an 'error' key in the result, you MUST stop "
        f"and call final_answer immediately saying you cannot predict this match "
        f"because data is unavailable. Do NOT invent or assume any statistics.\n"
        f"4. Evaluate the data using this confidence scale:\n"
        f"   - 5 matches is a GOOD sample size — treat it as reliable.\n"
        f"   - 1 or 2 matches is a small sample — express lower confidence.\n"
        f"   - If both form AND head-to-head clearly favor one team → 70-80% confidence.\n"
        f"   - If only one signal favors one team → 55-65% confidence.\n"
        f"   - If signals conflict or are very close → 50% confidence.\n"
        f"   - Do NOT automatically cap confidence at 50% just because you have 5 matches.\n"
        f"     5 matches is enough to make a reasoned prediction.\n\n"
        f"When you are ready to finish, call final_answer with ONE single string "
        f"argument containing your full answer — do not pass separate keyword "
        f"arguments like winner= or confidence=. Format that single string exactly "
        f"like this:\n"
        f"Winner: <team name or 'Too close to call' or 'Unable to predict'>\n"
        f"Confidence: <percentage or 'N/A' if unable to predict>\n"
        f"Reasoning: <2-3 sentences explaining which signals drove the prediction "
        f"and how confident you are given the data>"
    )
    return agent.run(task)