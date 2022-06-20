from pydantic import BaseModel


class UserBase(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": 1,
                "username": "username"
            }
        }


class UserCreate(BaseModel):
    username: str
    password: str

    class Config:
        schema_extra = {
            "example": {
                "username": "username",
                "password": "password"
            }
        }


class UserLogin(BaseModel):
    username: str
    password: str

    class Config:
        schema_extra = {
            "example": {
                "username": "username",
                "password": "password"
            }
        }


class UserDB(UserBase):
    password: str

    class Config:
        schema_extra = {
            "example": {
                **UserBase.Config.schema_extra.get("example"),
                "password": "password"
            }
        }
