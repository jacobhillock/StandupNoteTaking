from pydantic import BaseModel


class UpdateNotesModel(BaseModel):
    name: str
    date: str = ""
    note: str = ""
