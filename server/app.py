import logging
import os
import psutil
import uuid
from fastapi import FastAPI, BackgroundTasks, HTTPException, Response, Request, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordBearer
from google.oauth2 import id_token
from google.auth.transport import requests
from models import URLRequest, URLResponse, StatusResponse
from audio import generate_audio_task

from models import TokenVerificationRequest
from readers import substack, articles
from utils import estimate_processing_time, get_domain

from database import DatabaseManager
from rss_manager import get_rss_content

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

GOOGLE_CLIENT_ID = "213491127239-lssh5snpejuob32apcpjecnvf1i7ceng.apps.googleusercontent.com"

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    # Allow your frontend origin
    allow_origins=[
        "http://localhost:3000",
        "http://157.245.72.83:3000",
        "https://157.245.72.83:3000",
        "http://article2audio.com",
        "http://www.article2audio.com",
        "https://article2audio.com",
        "https://www.article2audio.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"]
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

tasks = {}

db_manager = DatabaseManager()

def print_memory_usage():
    # Get current memory usage
    process = psutil.Process()
    memory_info = process.memory_info()
    print(f"Current memory usage: {memory_info.rss / (1024 * 1024):.2f} MB")


async def get_current_user(request: Request):
    authorization: str = request.headers.get('Authorization')
    logging.info(f"Authorization header: {authorization}")
    if authorization is None:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    if not authorization.startswith('Bearer '):
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")
    token = authorization[len('Bearer '):]
    try:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID, clock_skew_in_seconds=15)
        return idinfo
    except ValueError as e:
        logging.error(f"Token verification failed: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid token")


@app.post("/api/verify_token")
async def verify_token(request: TokenVerificationRequest):
    try:
        logging.info(f"Verifying token: {request.token[:10]}...")
        idinfo = id_token.verify_oauth2_token(
            request.token,
            requests.Request(),
            GOOGLE_CLIENT_ID,
            clock_skew_in_seconds=15
        )

        logging.info(f"Token verified. User info: {idinfo}")
        userid = idinfo['sub']
        name = idinfo.get("name")
        email = idinfo.get("email")

        db_manager.get_or_create_user(userid, name=name, email=email)

        return {"userid": userid, "email": email}
    except ValueError as e:
        logging.error(f"Token verification failed: {str(e)}")
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")


@app.post("/api/process_article", response_model=URLResponse)
async def process_article(
        request: URLRequest,
        background_tasks: BackgroundTasks,
        current_user: dict = Depends(get_current_user)
):
    url = request.url
    domain = get_domain(url)
    logging.info(f"Domain extracted: {domain}")

    try:
        if "substack.com" in domain:
            scraper = substack.SubstackScraper()
        else:
            scraper = articles.ArticleReader()

        task_id = str(uuid.uuid4())

        tasks[task_id] = {'status': 'scraping_url'}

        text = scraper.get_post_content(url)
        # TODO: Add error handling in case these are None or ""
        article_name = scraper.get_article_name(url)
        author_name = scraper.get_author_name(url)
        del scraper  # Clean up the scraper object
        if not text:
            raise ValueError("No content found at the provided URL.")

        estimated_time = estimate_processing_time(text)

        tasks[task_id] = {'status': 'Creating audio file...', 'article_name': article_name, 'author_name': author_name}

        user_id = current_user['sub']
        given_name = current_user['given_name']

        background_tasks.add_task(
            generate_audio_task, text, article_name, author_name, tasks, task_id, user_id, given_name
        )

        logging.info(f"Returning response with estimated_time: {estimated_time} and task_id: {task_id}")
        return URLResponse(estimated_time=estimated_time, task_id=task_id)
    except Exception as e:
        logging.error(f"Error processing article: {e}")
        error_message = str(e) or "Failed to process the URL. Please check the URL and try again."
        raise HTTPException(status_code=400, detail=error_message)


@app.get("/api/status/{task_id}", response_model=StatusResponse)
async def get_status(task_id: str):
    print(f"Tasks: {tasks}")
    print(f"Checking status for task_id: {task_id}")
    print_memory_usage()
    task = tasks.get(task_id)
    if not task:
        print(f"Task not found for task_id: {task_id}")
        raise HTTPException(status_code=404, detail="Task not found")
    print(f"Task found: {task}")
    return StatusResponse(**task)


@app.get("/api/download/{file_id}")
async def download_file(file_id: int, current_user: dict = Depends(get_current_user)):
    user_id = current_user['sub']
    audio_file = db_manager.get_audio_file(file_id, user_id)
    if not audio_file:
        raise HTTPException(status_code=404, detail="File not found")
    file_path = audio_file.file_path
    file_name = audio_file.file_name
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    headers = {'Content-Disposition': f'attachment; filename="{file_name}"'}
    return FileResponse(file_path, media_type='application/octet-stream', headers=headers)


@app.get("/api/audio_files")
async def list_audio_files(current_user: dict = Depends(get_current_user)):
    print("current user /api/audio_files: ", current_user)
    user_id = current_user['sub']
    print("user id get audio files", user_id)
    files = db_manager.list_audio_files(user_id)
    return [
        {"id": file.id, "file_name": file.file_name, "creation_date": file.creation_date}
        for file in files
    ]


@app.api_route("/rss.xml", methods=["GET", "HEAD"])
async def rss_feed(request: Request):
    content = get_rss_content()
    headers = {"Content-Type": "application/rss+xml"}

    if request.method == "HEAD":
        return Response(content="", headers=headers)
    else:
        return Response(content=content, headers=headers, media_type="application/rss+xml")


@app.get("/rss/{user_id}.xml")
async def rss_feed(user_id: str):
    content = get_rss_content(user_id)
    headers = {"Content-Type": "application/rss+xml"}
    return Response(content=content, headers=headers, media_type="application/rss+xml")


@app.get("/api/get_feed_url")
async def get_feed_url(current_user: dict = Depends(get_current_user)):
    user_id = current_user['sub']
    # feed_url = f"https://article2audio.com/rss/{user_id}.xml"
    feed_url = f"http://localhost:3000/rss/{user_id}.xml"
    return {"feed_url": feed_url}


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
