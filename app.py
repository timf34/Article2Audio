import logging

from flask import Flask, render_template, request, redirect, url_for, send_file
from openai import OpenAI
from urllib.parse import urlparse

from audio import *
from config import OPENAI_KEY, LOGIN_PASSWORD
from readers import substack, articles


app = Flask(__name__)
client = OpenAI(api_key=OPENAI_KEY)
DEVELOPMENT: bool = False


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


@app.route('/home', methods=['GET', 'POST'])
def home():
    try:
        if request.method == 'POST':
            url = request.form['url']
            domain = get_domain(url)
            # Log the domain to see what is being captured
            logging.info(f"Domain extracted: {domain}")

            if "substack.com" in domain:
                scraper = substack.SubstackScraper()
            else:
                scraper = articles.ArticleReader()

            text = scraper.get_post_content(url)
            estimated_time = estimate_processing_time(text)
            # audio_segments = generate_audio(client, text)
            # merged_audio = merge_audio_segments(audio_segments)
            # temp_file_path = save_audio_to_temp_file(merged_audio)
            temp_file_path = "speech.mp3"
            logging.info(f"Processing time: {estimated_time}, File: {temp_file_path}")

            return send_file(temp_file_path, mimetype='audio/mpeg', as_attachment=True, download_name='audio.mp3')

        return render_template('home.html', estimated_time=None)

    except Exception as e:
        logging.error(f"Error during POST to /home: {e}")
        return str(e), 500  # Return the error and a server error status


if __name__ == '__main__':
    app.run(debug=True)
