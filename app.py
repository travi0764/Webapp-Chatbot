from fastapi import FastAPI, Request, File, UploadFile
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from routers.processingUpload import processUploads

from typing import List
from utils.logger import logging
from dotenv import load_dotenv
from routers.stream import response_generator

load_dotenv()

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return HTMLResponse(content=open("static/index.html", "r").read(), status_code=200)


@app.get("/upload", response_class=HTMLResponse)
async def upload(request: Request):
    return HTMLResponse(content=open("static/upload.html", "r").read(), status_code=200)

@app.get("/ask-question")
@app.post("/ask-question")
async def ask_question(question: str):

    # question_text = question.get('question')
    logging.info(f"Query receieved: {question}")
    return StreamingResponse(response_generator(question), media_type='text/event-stream')

@app.post("/upload-data")
async def upload_data(files: List[UploadFile] = File(...)):
    res = processUploads(files)
    return res

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080, log_level="info")
