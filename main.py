from googlesearch import search
from typing import Union, List
from fastapi import FastAPI
from pydantic import BaseModel
from youtube_transcript_api import YouTubeTranscriptApi
from python_yt_search import VideosSearch, PlaylistsSearch, Search
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    '*'
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/search/{query}")
def search_query(query: str):
    return [x for x in search(query, advanced=True, num_results=20)]

class SearchQuery(BaseModel):
    query: str
    nodeId: int

class SearchQueries(BaseModel):
    data: List[SearchQuery]

@app.get("/youtube/{video_id}")
def getTranscript(video_id: str):
    return " ".join(x["text"] for x in YouTubeTranscriptApi.get_transcript(video_id))
