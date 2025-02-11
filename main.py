from googlesearch import search
from typing import Union, List
from fastapi import FastAPI
from pydantic import BaseModel
from youtube_transcript_api import YouTubeTranscriptApi

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/search/{query}")
def search_query(query: str):
    return [x for x in search(query, advanced=True)]

class SearchQuery(BaseModel):
    query: str
    nodeId: int

class SearchQueries(BaseModel):
    data: List[SearchQuery]

@app.get("/youtube/{video_id}")
def getTranscript(video_id: str):
    return " ".join(x["text"] for x in YouTubeTranscriptApi.get_transcript(video_id))



# @app.post("/searchbatch")
# def search_batch(queries: SearchQueries):
#     results = []
#     for query in queries.data:
#         results.append({
#             "nodeId": query.nodeId,
#             "results": [x for x in search(query.query)]
#         })
#     return results

