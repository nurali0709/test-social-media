from pydantic import BaseModel

class PostSchema(BaseModel):
    title: str
    description: str
