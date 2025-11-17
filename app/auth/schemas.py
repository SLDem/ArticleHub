from pydantic import BaseModel


class RegisterSchema(BaseModel):
    email: str
    password: str
    name: str

class LoginSchema(BaseModel):
    email: str
    password: str
