'''Base Pydantic Model'''
from pydantic import BaseModel

class PostSchema(BaseModel):
    '''Schema for posting'''
    title: str
    description: str

