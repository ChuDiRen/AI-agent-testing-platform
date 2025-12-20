from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class ApiDoc(SQLModel, table=True):
    __tablename__ = "api_doc"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(index=True)
    doc_name: str = Field(max_length=200)
    doc_type: str = Field(max_length=50)
    doc_content: Optional[str] = Field(default=None)
    doc_format: Optional[str] = Field(default="markdown", max_length=50)
    doc_version: Optional[str] = Field(default="1.0.0", max_length=50)
    doc_desc: Optional[str] = Field(default=None, max_length=500)
    create_time: Optional[datetime] = Field(default_factory=datetime.now)
    update_time: Optional[datetime] = Field(default_factory=datetime.now)
