from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    refresh_token: str

    class Config:
        schema_extra = {
            "example": {
                "access_token": "access_token",
                "refresh_token": "refresh_token"
            }
        }
