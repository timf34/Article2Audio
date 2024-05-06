import logging
import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, send_file, jsonify
from flask_executor import Executor
from urllib.parse import urlparse

from config import OPENAI_KEY, LOGIN_PASSWORD, SECRET_KEY, AUDIO_FILE_NAME
from audio import generate_audio, merge_audio_segments, save_audio_file
from readers import substack, articles
from openai import OpenAI

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['EXECUTOR_TYPE'] = 'thread'
executor = Executor(app)

DEVELOPMENT = False

client = OpenAI(api_key=OPENAI_KEY)

# Global dictionary to store audio file paths
audio_file_paths = {'audio_file_path': AUDIO_FILE_NAME}
audio_file_info = {'last_modified': ""}


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
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('home.html', estimated_time=None)


@app.route('/check_audio_ready', methods=['GET'])
def check_audio_ready():
    if "audio_file_path" in audio_file_paths:
        file_path = audio_file_paths["audio_file_path"]
        return jsonify(
            {
                'is_ready': True,
                'file_path': url_for('download_audio', path=file_path),
                'last_modified': audio_file_info['last_modified']
            }
        )
    return jsonify({'is_ready': False})


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

        # Start the audio generation in the background
        executor.submit(stub_generate_audio, text)

        return render_template('home.html', estimated_time=estimated_time)
    except Exception as e:
        error_message = str(e) or "Failed to process the URL. Please check the URL and try again."
        return render_template('home.html', error=error_message, url=url)


def stub_generate_audio(text):
    if DEVELOPMENT:
        temp_file_path = "speech.mp3"
    else:
        audio_segments = generate_audio(client, text)
        merged_audio = merge_audio_segments(audio_segments)
        audio_file_info['last_modified'] = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        save_audio_file(merged_audio)

        # Get current working directory
        pwd = os.getcwd()
        logging.info(f"Audio file saved in {pwd} as {AUDIO_FILE_NAME}")



@app.route('/download_audio', methods=['GET'])
def download_audio():
    if file_path := audio_file_paths.get('audio_file_path'):
        return send_file(file_path, mimetype='audio/mpeg', as_attachment=True, download_name='audio.mp3')
    return "No audio file found.", 404


if __name__ == '__main__':
    app.run(debug=True)