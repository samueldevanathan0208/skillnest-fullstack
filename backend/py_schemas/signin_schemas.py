from pydantic import BaseModel
from typing import Optional

class CreateUser(BaseModel):
    user_name: str
    user_email: str
    user_password: str
    user_dateofbirth: str
    user_phone: str
    user_gender: str

class LoginRequest(BaseModel):
    user_email: str
    user_password: str

class UpdateUser(BaseModel):
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    user_dateofbirth: Optional[str] = None
    user_phone: Optional[str] = None
    user_gender: Optional[str] = None

class DeleteUserRequest(BaseModel):
    password: str
