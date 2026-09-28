import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

class AnalysisResultOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    result: str
    confidence: float
    created_at: datetime