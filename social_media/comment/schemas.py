'''Base pydantic model'''
from pydantic import BaseModel

class CommentCreate(BaseModel):
    '''Validation for Comment'''
    text: str

    class Config:
        '''Enabling ORM mode to Comment model'''
        orm_mode = True

class CommentResponseCreate(BaseModel):
    '''Validation for Comment Response'''
    text: str

    class Config:
        '''Enabling ORM mode to CommentResponse model'''
        orm_mode = True
