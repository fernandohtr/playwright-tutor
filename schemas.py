from typing import Dict, Optional, Union
from pydantic import BaseModel


class Entry(BaseModel):
    process_number: str


class FirstInstance(BaseModel):
    classe: str
    assunto: str
    foro: str
    vara: str


class SecondInstance(BaseModel):
    classe: str
    assunto: str
    secao: str
    orgao: str
    area: str


class ProcessInfo(BaseModel):
    first_instance: Optional[FirstInstance] = None
    second_instance: Optional[SecondInstance] = None


class ErrorMessage(BaseModel):
    error: str
