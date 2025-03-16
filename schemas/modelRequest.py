from pydantic import BaseModel
from typing import Optional


class ModelRequestDTO(BaseModel):
    modelId: Optional[int] = None
    modelName: str
    modelDescription: Optional[str] = None
    modelOverviewMarkdown: Optional[str] = None
    modelFrame: Optional[str] = None
    imageId: int
    isPublic: int
    modelPath: Optional[str] = None
    userId: str
