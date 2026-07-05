from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent import predict_with_agent

app = FastAPI(title="VerdictIQ API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class PredictRequest(BaseModel):
    team1: str
    team2: str

class PredictResponse(BaseModel):
    team1: str
    team2: str
    winner: str
    confidence: str
    reasoning: str

def parse_agent_response(raw: str, team1: str, team2: str) -> dict:
    """
    Parses the agent's plain-text response into structured fields.
    Expected format:
        Winner: Argentina
        Confidence: 65%
        Reasoning: Some explanation here.
    """
    result = {
        "team1": team1,
        "team2": team2,
        "winner": "Unable to predict",
        "confidence": "N/A",
        "reasoning": raw.strip(),
    }

    for line in raw.strip().splitlines():
        line = line.strip()
        if line.lower().startswith("winner:"):
            result["winner"] = line.split(":", 1)[1].strip()
        elif line.lower().startswith("confidence:"):
            result["confidence"] = line.split(":", 1)[1].strip()
        elif line.lower().startswith("reasoning:"):
            result["reasoning"] = line.split(":", 1)[1].strip()

    return result

@app.get("/")
def health_check():
    return {"status": "VerdictIQ backend is running"}

@app.post("/predict", response_model=PredictResponse)
def predict_match(request: PredictRequest):
    team1 = request.team1.strip()
    team2 = request.team2.strip()

    if not team1 or not team2:
        raise HTTPException(
            status_code=400,
            detail="Both team1 and team2 are required."
        )

    if team1.lower() == team2.lower():
        raise HTTPException(
            status_code=400,
            detail="team1 and team2 must be different teams."
        )

    try:
        raw = predict_with_agent(team1, team2)
        return parse_agent_response(raw, team1, team2)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )