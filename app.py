from fastapi import FastAPI, Request, File, UploadFile, HTTPException, Form, Depends
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from routers.processingUpload import processUploads
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from utils.logger import logging
from dotenv import load_dotenv
from routers.stream import response_generator
import uuid

load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")

PASSWORD = "b94d27b9-fdec-11ec-9d64-0242ac120002"  # Set your desired password here

# Function to authenticate password
def authenticate_password(password: str):
    if password != PASSWORD:
        logging.error("Invalid Password.")
        raise HTTPException(
            status_code=401,
            detail="Invalid password",
        )
    return True

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    response = HTMLResponse(content=open("static/index.html", "r").read(), status_code=200)
    return response

@app.get("/upload", response_class=HTMLResponse)
async def upload(request: Request):
    response = HTMLResponse(content=open("static/upload.html", "r").read(), status_code=200)
    return response

@app.get("/ask-question")
@app.post("/ask-question")
async def ask_question(request: Request, question: str, session_id: str = "abcde"):
    logging.info(f"Query received from session {session_id}: {question}")
    response = response_generator(question, session_id)
    return StreamingResponse(response, media_type='text/event-stream')

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

# Health API
@app.get("/health", response_model=dict)
async def health():
    return JSONResponse(content={"status": "running"}, status_code=200)

# Greeting API
@app.get("/greeting", response_model=dict)
async def greeting():
    return JSONResponse(content={"message": "Hi, I am SIH Chatbot, How can I help you ?"}, status_code=200)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080, log_level="info")
