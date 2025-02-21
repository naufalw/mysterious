from googlesearch import search
from typing import Union, List
from fastapi import FastAPI
from pydantic import BaseModel
from youtube_transcript_api import YouTubeTranscriptApi
from python_yt_search import VideosSearch, PlaylistsSearch, Search

app = FastAPI()

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

# @app.get("/search/{query}")
# async def getTranscript(query: str):
#     videos = VideosSearch(query, limit = 3)
#     playlist = PlaylistsSearch(query, limit = 2)

#     res_videos = [{"url":v["link"], "title": v["title"], "description": " ".join([x["text"] for x in v["descriptionSnippet"]])} for v in videos.result()["result"]]
#     res_playlist = [{"url":v["link"], "title": v["title"], "description": " ".join([x["text"] for x in v["descriptionSnippet"]])} for v in playlist.result()["result"]]

#     allSearch = Search(query, limit = 10)

#     return allSearch.result()



# @app.post("/searchbatch")
# def search_batch(queries: SearchQueries):
#     results = []
#     for query in queries.data:
#         results.append({
#             "nodeId": query.nodeId,
#             "results": [x for x in search(query.query)]
#         })
#     return results

