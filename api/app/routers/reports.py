from fastapi import APIRouter
from typing import Dict, Any
from app.agent.graph import ReportsAgent
import os

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/summary")
async def get_summary_report() -> Dict[str, Any]:
    """Generate AI-powered summary report or heuristic fallback"""
    llm_provider = os.getenv("LLM_PROVIDER", "none")

    if llm_provider != "none":
        # Use LangGraph agent
        agent = ReportsAgent()
        summary = await agent.generate_summary()
    else:
        # Use heuristic fallback
        from app.agent.heuristics import generate_heuristic_summary
        summary = generate_heuristic_summary()

    return {
        "summary": summary,
        "generated_with": "ai" if llm_provider != "none" else "heuristics",
        "provider": llm_provider
    }