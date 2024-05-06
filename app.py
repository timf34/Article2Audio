import logging
from flask import Flask, render_template, request, redirect, url_for, session, send_file, jsonify, copy_current_request_context
from flask_executor import Executor
from urllib.parse import urlparse

from config import OPENAI_KEY, LOGIN_PASSWORD
from audio import generate_audio, merge_audio_segments, save_audio_to_temp_file
from readers import substack, articles
from openai import OpenAI

app = Flask(__name__)
app.secret_key = "super secret key"
app.config['EXECUTOR_TYPE'] = 'thread'
executor = Executor(app)

DEVELOPMENT = True

client = OpenAI(api_key=OPENAI_KEY)

# Global dictionary to store audio file paths
audio_file_paths = {}


def estimate_processing_time(text) -> float:
    return len(text) * 0.05


def get_domain(url) -> str:
    parsed_url = urlparse(url)
    return parsed_url.netloc


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form['password']
        if password == LOGIN_PASSWORD:
            return redirect(url_for('home'))
        else:
            return "Invalid password"
    return render_template('login.html')


@app.route('/home', methods=['GET'])
def home():
    return render_template('home.html', estimated_time=None)


@app.route('/check_audio_ready', methods=['GET'])
def check_audio_ready():
    if "audio_file_path" in audio_file_paths:
        file_path = audio_file_paths["audio_file_path"]
        return jsonify({'is_ready': True, 'file_path': url_for('download_audio', path=file_path)})
    return jsonify({'is_ready': False})


@app.route('/process_article', methods=['POST'])
def process_article():
    url = request.form['url']
    domain = get_domain(url)
    logging.info(f"Domain extracted: {domain}")

    if "substack.com" in domain:
        scraper = substack.SubstackScraper()
    else:
        scraper = articles.ArticleReader()

    text = scraper.get_post_content(url)
    estimated_time = estimate_processing_time(text)

    # Start the audio generation in the background
    executor.submit(stub_generate_audio, text)

    return render_template('home.html', estimated_time=estimated_time)


def stub_generate_audio(text):
    if DEVELOPMENT:
        temp_file_path = "speech.mp3"
    else:
        audio_segments = generate_audio(client, text)
        merged_audio = merge_audio_segments(audio_segments)
        temp_file_path = save_audio_to_temp_file(merged_audio)

    audio_file_paths['audio_file_path'] = temp_file_path  # Save the path for download


@app.route('/download_audio', methods=['GET'])
def download_audio():
    if file_path := audio_file_paths.get('audio_file_path'):
        return send_file(file_path, mimetype='audio/mpeg', as_attachment=True, download_name='audio.mp3')
    return "No audio file found.", 404


if __name__ == '__main__':
    app.run(debug=True)
