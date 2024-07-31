from fastapi import FastAPI

from .common import Entry

from .app import main as collector

app = FastAPI()


@app.post("/")
async def main(entry: Entry):
    result = await collector(entry)
    return result
