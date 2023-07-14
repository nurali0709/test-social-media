'''Base Pydantic Model'''
from pydantic import BaseModel

class PostSchema(BaseModel):
    '''Schema for posting'''
    title: str
    description: str

class SubscriptionSchema(BaseModel):
    subscribed_to_id: int

    class Config:
        orm_mode = True
