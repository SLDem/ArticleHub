from pydantic import BaseModel
from typing import List, Optional


class ArticleCreateSchema(BaseModel):
    title: str
    content: str
    tags: List[str] = []

class ArticleUpdateSchema(BaseModel):
    title: Optional[str]
    content: Optional[str]
