from googlesearch import search
from typing import Union, List
from fastapi import FastAPI
from pydantic import BaseModel
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from fastapi.middleware.cors import CORSMiddleware
from free_proxy_manager import FreeProxyManager

app = FastAPI()
proxy_manager = FreeProxyManager()

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

@app.get('/update')
def update():
    proxy_manager.update_proxy_list()
    return {"message": "Proxy list updated"}

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
    def get_transcript_with_proxy():
        proxy = proxy_manager.get_proxy()
        if not proxy:
            raise Exception("No working proxies available")
            
        try:
            transcript = YouTubeTranscriptApi.get_transcript(
                video_id,
                proxies=proxy
            )
            return " ".join(x["text"] for x in transcript)
        except Exception as e:
            proxy_manager.remove_and_update_proxy(proxy)
            raise e

    # Try with proxy first, if it fails, try without proxy
    try:
        return get_transcript_with_proxy()
    except Exception as e:
        # Fallback to direct connection if proxy fails
        return " ".join(x["text"] for x in YouTubeTranscriptApi.get_transcript(video_id))
