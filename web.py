import re

from typing import Dict, Union
from fastapi import FastAPI, Query, HTTPException, status

from .schemas import Entry, ProcessInfo
from .app import main as collector

app = FastAPI()


@app.get("/", status_code=status.HTTP_200_OK, response_model=ProcessInfo)
async def main(process_number: str = Query(..., alias="q")) -> ProcessInfo:
    entry = Entry(process_number=process_number)
    result = await collector(entry)

    pattern = re.compile(r"^\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}$")

    if not pattern.match(process_number):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Process number must have this parttern: XXXXXXX-XX.XXXX.X.XX.XXXX",
        )
    elif hasattr(result, "first_instance") and (not result.first_instance and not result.second_instance):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Process number {process_number} not found",
        )
    return result
