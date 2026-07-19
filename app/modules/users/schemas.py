from pydantic import BaseModel

class UserAuth(BaseModel):
    user_name: str
    password: str

class UserCreateAdmin(UserAuth):
    is_admin: bool = False

class UserInDB(BaseModel):
    id: int
    user_name: str
    is_admin: bool

    class Config:
        from_attributes = True
