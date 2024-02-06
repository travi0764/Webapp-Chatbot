from fastapi import FastAPI, Request, File, UploadFile, HTTPException, Form
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

PASSWORD = "b94d27b9-fdec-11ec-9d64-0242ac120002"  # Set your desired password here

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
    logging.info(f"Query received: {question}")
    return StreamingResponse(response_generator(question), media_type='text/event-stream')

def authenticate_password(password: str):
    if password != PASSWORD:
        logging.error("Invalid Password.")
        raise HTTPException(
            status_code=401,
            detail="Invalid password",
        )
    return True

@app.post("/upload-data")
async def upload_data(files: List[UploadFile] = File(...), password: str = Form(...)):
    # logging.info(f"File uploaded: {files.filename}")
    if not password:
        logging.info('No Password.')
        raise HTTPException(
            status_code=401,
            detail="Password is required",
        )
    
    authenticate_password(password)
    
    res = processUploads(files)
    return res

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080, log_level="info")
