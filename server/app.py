import logging
import os
import uuid
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from models import URLRequest, URLResponse, StatusResponse
from audio import generate_audio_task
from readers import substack, articles
from utils import estimate_processing_time, get_domain

app = FastAPI()

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

@app.post("/api/process_article", response_model=URLResponse)
async def process_article(request: URLRequest, background_tasks: BackgroundTasks):
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

        tasks[task_id] = {'status': 'creating_audio_file', 'article_name': article_name, 'author_name': author_name}
        background_tasks.add_task(generate_audio_task, text, article_name, author_name, tasks, task_id)

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
    task = tasks.get(task_id)
    if not task:
        print(f"Task not found for task_id: {task_id}")
        raise HTTPException(status_code=404, detail="Task not found")
    print(f"Task found: {task}")
    return StatusResponse(**task)


@app.get("/api/download/{task_id}")
async def download_file(task_id: str):
    task = tasks.get(task_id)
    if not task or task['status'] != 'completed':
        raise HTTPException(status_code=404, detail="File not ready")
    file_path = task.get('file_path')
    file_name = task.get('file_name')
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    headers = {'Content-Disposition': f'attachment; filename="{file_name}.mp3"'}  # Explicitly setting content disposition
    return FileResponse(file_path, media_type='application/octet-stream', headers=headers)


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
