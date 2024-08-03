from typing import Dict, Union
from fastapi import FastAPI, Query, HTTPException, status

from .schemas import Entry, ProcessInfo
from .app import main as collector

app = FastAPI()


@app.get("/", status_code=status.HTTP_200_OK, response_model=ProcessInfo)
async def main(process_number: str = Query(..., alias="q")) -> ProcessInfo:
    entry = Entry(process_number=process_number)
    result = await collector(entry)
    if hasattr(result, "first_instance") and (not result.first_instance and not result.second_instance):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Process number {process_number} not found",
        )
    elif hasattr(result, "error"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=result.error,
        )
    return result
