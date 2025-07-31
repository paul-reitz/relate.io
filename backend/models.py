from pydantic import BaseModel

class Client(BaseModel):
    id: int
    name: str
    email: str
    portfolio_value: float

class Feedback(BaseModel):
    client_id: int
    text: str