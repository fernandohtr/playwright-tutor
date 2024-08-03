from http import HTTPStatus
from fastapi import FastAPI, Query

from .schemas import Entry, ProcessInfo
from .app import main as collector

app = FastAPI()


@app.get("/", status_code=HTTPStatus.OK, response_model=ProcessInfo)
async def main(process_number: str = Query(..., alias="q")):
    entry = Entry(process_number=process_number)
    result = await collector(entry)
    return result
