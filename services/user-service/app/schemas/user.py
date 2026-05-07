from pydantic import BaseModel


class UserResponse(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True
