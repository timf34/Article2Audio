import logging

from flask import Flask, render_template, request, redirect, url_for, send_file
from openai import OpenAI
from urllib.parse import urlparse

from audio import *
from config import OPENAI_KEY, LOGIN_PASSWORD
from readers import substack, articles


app = Flask(__name__)
client = OpenAI(api_key=OPENAI_KEY)
DEVELOPMENT: bool = True


def estimate_processing_time(text) -> float:
    # Assume each character takes 0.05 seconds to process
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
    return render_template('home.html', estimated_time=None, file_path=None)


@app.route('/process_audio', methods=['POST'])
def process_audio():
    try:
        url = request.form['url']
        domain = get_domain(url)
        logging.info(f"Domain extracted: {domain}")

        if "substack.com" in domain:
            scraper = substack.SubstackScraper()
        else:
            scraper = articles.ArticleReader()

        text = scraper.get_post_content(url)
        estimated_time = estimate_processing_time(text)

        if DEVELOPMENT is True:
            temp_file_path = "speech.mp3"
        else:
            audio_segments = generate_audio(client, text)
            merged_audio = merge_audio_segments(audio_segments)
            temp_file_path = save_audio_to_temp_file(merged_audio)

        logging.info(f"Processing time: {estimated_time}, File: {temp_file_path}")

        return render_template('home.html', estimated_time=estimated_time, file_path=temp_file_path)

    except Exception as e:
        logging.error(f"Error during POST to /process_audio: {e}")
        return str(e), 500  # Return the error and a server error status


@app.route('/download_audio')
def download_audio():
    if file_path := request.args.get('file_path'):
        return send_file(file_path, mimetype='audio/mpeg', as_attachment=True, download_name='audio.mp3')
    else:
        return "No audio file found.", 404


if __name__ == '__main__':
    app.run(debug=True)
    