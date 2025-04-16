from pydantic import BaseModel, Field, EmailStr
from fastapi import UploadFile, File, Query

class DelUser(BaseModel):
    login: str = Field(min_length=4, max_length=16)

class SetPermissions(BaseModel):
    permission: str
    permission_status: bool
    login: str = Field(min_length=4, max_length=16)

class CreateUser(BaseModel):
    login: str = Field(min_length=4, max_length=16)
    password: str = Field(min_length=6, max_length=32)
    mail: EmailStr

class AuthUser(BaseModel):
    login: str = Field(min_length=4, max_length=16)
    password: str = Field(min_length=6, max_length=32)
