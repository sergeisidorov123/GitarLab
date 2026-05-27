from pydantic import BaseModel


class UserResponse(BaseModel):
    id: int
    username: str
    role_name: str
    is_admin: bool

    class Config:
        orm_mode = True
