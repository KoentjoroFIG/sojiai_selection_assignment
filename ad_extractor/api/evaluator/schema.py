from typing import Optional
from pydantic import BaseModel, Field

from api.schema import EvaluationResult

class EvaluationResponse(BaseModel):
    status: str = Field(..., description="Evaluation status: 'success' or 'failure'")
    evaluation_results: Optional[list[EvaluationResult]] = Field(None, description="List of evaluation results for the provided aircraft configurations")