from pydantic import BaseModel

class CommentCreate(BaseModel):
    text: str

    class Config:
        orm_mode = True
