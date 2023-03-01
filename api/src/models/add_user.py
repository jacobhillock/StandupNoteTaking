from pydantic import BaseModel


class AddUserModel(BaseModel):
    name: str
