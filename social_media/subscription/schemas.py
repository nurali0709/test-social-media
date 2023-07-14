from pydantic import BaseModel

class SubscriptionSchema(BaseModel):
    subscribed_to_id: int

    class Config:
        orm_mode = True
