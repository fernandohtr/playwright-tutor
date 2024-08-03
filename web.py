from http import HTTPStatus
from typing import Dict, Union
from fastapi import FastAPI, Query

from .schemas import Entry, ProcessInfo, ErrorMessage
from .app import main as collector

app = FastAPI()


@app.get("/", status_code=HTTPStatus.OK, response_model=Union[ProcessInfo, ErrorMessage])
async def main(process_number: str = Query(..., alias="q")) -> Union[ProcessInfo, ErrorMessage]:
    entry = Entry(process_number=process_number)
    result = await collector(entry)
    return result
