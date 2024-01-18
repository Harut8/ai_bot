from fastapi import FastAPI

from app.helper import process_input_with_retrieval
from app.scrapping import Scrapping

app = FastAPI()


@app.post("/vectorize-url-data")
async def vectorize_url_data(url: str):
    await Scrapping.scrap(url)
    return {"message": "ok"}


@app.post("/get-top-3-similar-docs")
async def get_top_3_similar_docs(query_embedding):
    return {
        "answer": await process_input_with_retrieval(query_embedding)
    }
