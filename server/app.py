import logging
import uuid
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from models import URLRequest, URLResponse, StatusResponse
from audio import generate_audio_task
from readers import substack, articles
from utils import estimate_processing_time, get_domain

app = FastAPI()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

tasks = {}


@app.get("/api/get_task_id", response_model=URLResponse)
async def get_task_id():
    print("hello world task id")
    task_id = str(uuid.uuid4())
    tasks[task_id] = {'status': 'processing'}
    return URLResponse(hello="world")


@app.post("/api/process_article", response_model=URLResponse)
async def process_article(request: URLRequest):
    url = request.url
    domain = get_domain(url)
    logging.info(f"Domain extracted: {domain}")

    print("we in here")

    try:
        if "substack.com" in domain:
            scraper = substack.SubstackScraper()
        else:
            scraper = articles.ArticleReader()

        text = scraper.get_post_content(url)
        if not text:
            raise ValueError("No content found at the provided URL.")

        estimated_time = estimate_processing_time(text)

        task_id = str(uuid.uuid4())
        tasks[task_id] = {'status': 'processing'}
        # background_tasks.add_task(generate_audio_task, text, task_id)

        print(task_id)
        return URLResponse(estimated_time=estimated_time, task_id=task_id)
    except Exception as e:
        error_message = str(e) or "Failed to process the URL. Please check the URL and try again."
        raise HTTPException(status_code=400, detail=error_message)


@app.get("/api/status/{task_id}", response_model=StatusResponse)
async def get_status(task_id: str):
    task = tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.get("/api/download/{task_id}")
async def download_file(task_id: str):
    task = tasks.get(task_id)
    if not task or task['status'] != 'completed':
        raise HTTPException(status_code=404, detail="File not ready")
    return FileResponse(f"data/output/{task_id}.mp3", media_type='application/octet-stream', filename=f"{task_id}.mp3")


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
