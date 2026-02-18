from typing import Optional, List
from sqlmodel import Field, SQLModel, JSON
from datetime import datetime

class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    title: str
    scenes: List[dict] = Field(default=[], sa_type=JSON)
    status: str = Field(default="draft") # draft, generating, completed
    video_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
