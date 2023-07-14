'''Base Pydantic Model'''
from pydantic import BaseModel

class PostSchema(BaseModel):
    '''Schema for posting'''
    title: str
    description: str

class CommentCreate(BaseModel):
    text: str

    class Config:
        orm_mode = True

class SubscriptionSchema(BaseModel):
    subscriber_id: int
    subscribed_to_id: int

    class Config:
        orm_mode = True
