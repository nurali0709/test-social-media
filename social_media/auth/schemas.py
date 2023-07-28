'''Base Pydantic Model'''
from pydantic import BaseModel


class UserSignup(BaseModel):
    '''Schema for signing up user'''
    username: str
    email: str
    name: str
    surname: str
    password: str


class UserLogin(BaseModel):
    '''Schema for logging user in'''
    username: str
    password: str


class UserUpdate(BaseModel):
    '''Model for updating user data'''
    username: str
    email: str
    name: str
    surname: str
