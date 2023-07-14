'''Pydantic Base Model'''
from pydantic import BaseModel

class SubscriptionSchema(BaseModel):
    '''Validation for subscription'''
    subscribed_to_id: int

    class Config:
        '''Enabling ORM mode for subscription model'''
        orm_mode = True
