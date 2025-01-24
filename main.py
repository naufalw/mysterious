from googlesearch import search
from typing import Union
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/search/{query}")
def search_query(query: str):
    return [x for x in search(query)]

