import os
from typing import Dict, Any
from pydantic import BaseModel, Field
import json

from app.agent.models import get_chat_model
from app.services.etsy_client import EtsyClient
from app.services.aggregator import MetricsAggregator

# Simplified report state without TypedDict dependency
class ReportState:
    """State for the report generation"""
    def __init__(self):
        self.shop_id = ""
        self.raw_data = {}
        self.context = {}
        self.summary = ""
        self.insights = []
        self.recommendations = []
        self.error = ""

class ReportOutput(BaseModel):
    """Validated output from the agent"""
    summary: str = Field(description="Brief performance summary")
    insights: list = Field(description="Key insights from the data")
    recommendations: list = Field(description="Actionable recommendations")
    confidence: str = Field(description="Confidence level: high, medium, low")
    generated_with: str = Field(description="Generation method: ai or heuristics")

class ReportsAgent:
    """Simplified agent for generating shop reports"""

    def __init__(self):
        self.llm_provider = os.getenv("LLM_PROVIDER", "none")
        self.use_langsmith = os.getenv("LANGCHAIN_TRACING_V2", "false") == "true"

    async def generate_summary(self, shop_id: str = "demo_shop") -> Dict[str, Any]:
        """Generate summary report - currently uses heuristics fallback"""
        # For MVP, always use heuristics
        from app.agent.heuristics import generate_heuristic_summary
        return generate_heuristic_summary()

# Additional methods removed for MVP - will be restored when LangGraph is integrated