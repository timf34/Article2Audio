import logging
import os
from datetime import datetime
from time import sleep
from threading import Thread
from flask import Flask, render_template, request, redirect, url_for, session, send_file, jsonify
from urllib.parse import urlparse
from config import OPENAI_KEY, LOGIN_PASSWORD, SECRET_KEY, AUDIO_FILE_NAME, LAST_MODIFIED_FILE_NAME
from audio import generate_audio, merge_audio_segments, save_audio_file
from readers import substack, articles
from openai import OpenAI

app = Flask(__name__)
app.secret_key = SECRET_KEY

DEVELOPMENT = False

client = OpenAI(api_key=OPENAI_KEY)

def estimate_processing_time(text) -> int:
    return int(len(text) * 0.01) # 0.01 seconds per character

def get_domain(url) -> str:
    parsed_url = urlparse(url)
    return parsed_url.netloc

@app.route('/', methods=['GET', 'POST'])
def login():
    error=None
    if request.method == 'POST':
        password = request.form['password']
        if password == LOGIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('home'))
        else:
            error = "Invalid password"
    return render_template('login.html', error=error)

@app.route('/home', methods=['GET'])
def home():
    print("we are live")
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('home.html', estimated_time=None)

@app.route('/process_article', methods=['POST'])
def process_article():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    url = request.form['url']
    domain = get_domain(url)
    logging.info(f"Domain extracted: {domain}")

    try:
        if "substack.com" in domain:
            scraper = substack.SubstackScraper()
        else:
            scraper = articles.ArticleReader()

        text = scraper.get_post_content(url)
        if not text:
            raise ValueError("No content found at the provided URL.")

        estimated_time = estimate_processing_time(text)

        print("we in here")

        # Start the audio generation in the background
        thread = Thread(target=generate_audio_task, args=(text,))
        thread.start()

        print("after starting thread")

        return render_template('home.html', estimated_time=estimated_time)
    except Exception as e:
        error_message = str(e) or "Failed to process the URL. Please check the URL and try again."
        return render_template('home.html', error=error_message, url=url)

def generate_audio_task(text):
    print("in generate_audio_task")

    if DEVELOPMENT:
        temp_file_path = "speech.mp3"
    else:
        print("before generate audio")
        audio_segments = generate_audio(client, text)
        print("after generate audio")
        merged_audio = merge_audio_segments(audio_segments)
        print("after merge audio")
        with open(LAST_MODIFIED_FILE_NAME, 'w') as file:
            file.write(datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
        print("after write last modified")
        save_audio_file(merged_audio)
        print("after save audio file")

        # Get current working directory
        pwd = os.getcwd()
        print(f"Audio file saved in {pwd} as {AUDIO_FILE_NAME}")
        logging.info(f"Audio file saved in {pwd} as {AUDIO_FILE_NAME}")

def simple_task(duration):
    sleep(duration)
    print(f"Task completed after {duration} seconds")
    return f"Task completed after {duration} seconds"

@app.route('/run_simple_task', methods=['POST'])
def run_simple_task():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    duration = int(request.form['duration'])
    thread = Thread(target=simple_task, args=(duration,))
    thread.start()
    return jsonify({'status': 'Task started'}), 202

@app.route('/task_status/<task_id>')
def task_status(task_id):
    # Dummy endpoint for consistency
    return jsonify({'status': 'Use logs to track task completion'})


if __name__ == '__main__':
    app.run(debug=True)
