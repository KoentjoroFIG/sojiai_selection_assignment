from typing import Optional
from pydantic import BaseModel, Field

from api.schema import ADDocument


class ADExtractionResponse(BaseModel):
    status: str = Field(..., description="Extraction status: 'success' or 'failure'")
    extracted_ads: Optional[list[ADDocument]] = Field(None, description="Parsed AD document as a list")