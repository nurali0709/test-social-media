'''Base pydantic model'''
from pydantic import BaseModel

class CommentCreate(BaseModel):
    '''Validation for Comment'''
    text: str

    class Config:
        '''Enabling ORM mode to Comment model'''
        orm_mode = True
