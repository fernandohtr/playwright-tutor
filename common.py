from pydantic import BaseModel


class Entry(BaseModel):
    process_number: str
