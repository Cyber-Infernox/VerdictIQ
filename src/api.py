from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any

from agent import predict_with_agent

app = FastAPI(
    title="VerdictIQ API",
    version="1.0.0"
)

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
    winner: str
    confidence: int

    team1: Dict[str, Any]
    team2: Dict[str, Any]

    head_to_head: Optional[Dict[str, Any]]
    weights: Dict[str, float]

@app.get("/")
def health_check():
    return {
        "status": "VerdictIQ backend is running"
    }

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
        result = predict_with_agent(
            team1,
            team2
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )