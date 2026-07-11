from smolagents import LiteLLMModel, CodeAgent
from tools import (
    predict_match,
    fetch_recent_form,
    fetch_head_to_head,
)

model = LiteLLMModel(
    model_id="ollama_chat/gemma3:4b",
    api_base="http://127.0.0.1:11434",
    num_ctx=8192,
)

agent = CodeAgent(
    tools=[
        predict_match,
        fetch_recent_form,
        fetch_head_to_head,
    ],
    model=model,
)

def predict_with_agent(team1: str, team2: str) -> str:
    task = f"""
        You are an AI football analyst.

        Your goal is to predict the winner between '{team1}' and '{team2}'.

        IMPORTANT:
        The project's prediction engine is the source of truth.
        Do NOT calculate the winner yourself if the prediction engine is available.

        Workflow:

        1. Call predict_match("{team1}", "{team2}").
        2. If it returns:
        Winner = "Unable to Predict"
        then immediately call final_answer explaining that there is
        insufficient data to make a prediction.

        3. Optionally call:
        - fetch_recent_form("{team1}")
        - fetch_recent_form("{team2}")
        - fetch_head_to_head("{team1}", "{team2}")

        Use these ONLY to explain WHY the prediction engine reached its
        conclusion. Do NOT change or override the predicted winner.

        4. Produce a concise explanation.

        Finally call final_answer with ONE string exactly in this format:

        Winner: <winner returned by predict_match>

        Confidence: <confidence returned by predict_match>%

        Reasoning:
        <2-3 sentences explaining the recent form and head-to-head data that support the prediction. If head-to-head data is unavailable, mention that the prediction relied primarily on recent form.>

        Do not invent statistics.
        Do not modify the prediction engine's winner.
        Do not modify the confidence.
        """
    return agent.run(task)