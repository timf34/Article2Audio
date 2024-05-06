import tempfile

from flask import Flask, render_template, request, redirect, url_for, send_file
from io import BytesIO
from openai import OpenAI
from pydub import AudioSegment

from config import OPENAI_KEY
from readers import substack, articles
from urllib.parse import urlparse


app = Flask(__name__)
client = OpenAI(api_key=OPENAI_KEY)
DEVELOPMENT: bool = True


def estimate_processing_time(text) -> float:
    # Assume each character takes 0.05 seconds to process
    return len(text) * 0.05


def get_domain(url) -> str:
    parsed_url = urlparse(url)
    return parsed_url.netloc


def split_text_into_chunks(text, max_length=4096):
    words = text.split()
    chunks = []
    current_chunk = []

    for word in words:
        if len(" ".join(current_chunk)) + len(word) + 1 <= max_length:
            current_chunk.append(word)
        else:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form['password']
        if password == 'password':
            return redirect(url_for('home'))
        else:
            return "Invalid password"
    return render_template('login.html')


def generate_audio(text):
    chunks = split_text_into_chunks(text)
    audio_segments = []
    for chunk in chunks:
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=chunk
        )
        audio_data = BytesIO(response.content)
        audio_segments.append(AudioSegment.from_file(audio_data, format="mp3"))
    return audio_segments


def merge_audio_segments(audio_segments):
    merged_audio = AudioSegment.empty()
    for segment in audio_segments:
        merged_audio += segment
    return merged_audio


def save_audio_to_temp_file(merged_audio):
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
        merged_audio.export(temp_file.name, format="mp3")
        temp_file.seek(0)
        return temp_file.name


@app.route('/home', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        url = request.form['url']
        if DEVELOPMENT:
            audio_data = "speech.mp3"
            estimated_time = "1 minute 30 seconds"
            return render_template('home.html', estimated_time=estimated_time)
        else:
            domain = get_domain(url)
            if "substack.com" in domain:
                scraper = substack.SubstackScraper()
            else:
                scraper = articles.ArticleReader()

            text = scraper.get_post_content(url)
            estimated_time = estimate_processing_time(text)
            audio_segments = generate_audio(text)
            merged_audio = merge_audio_segments(audio_segments)
            temp_file_path = save_audio_to_temp_file(merged_audio)
            return send_file(temp_file_path, mimetype='audio/mpeg', as_attachment=True, download_name='audio.mp3'), render_template('home.html', estimated_time=estimated_time)

    # Initial GET request handling, show form without estimated time
    return render_template('home.html', estimated_time=None)




if __name__ == '__main__':
    app.run(debug=True)
