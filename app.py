from flask import Flask, render_template, request, redirect, url_for, send_file
from io import BytesIO
from openai import OpenAI
from config import OPENAI_KEY
from readers import substack

app = Flask(__name__)

client = OpenAI(api_key=OPENAI_KEY)

DEVELOPMENT: bool = True


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form['password']
        if password == 'password':
            return redirect(url_for('home'))
        else:
            return "Invalid password"
    return render_template('login.html')

@app.route('/home', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        url = request.form['url']
        if DEVELOPMENT:
            audio_data = "speech.mp3"
        else:
            scraper = substack.SubstackScraper()
            text = scraper.get_post_content(url)
            response = client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=text
            )
            audio_data = BytesIO(response.content)
        return send_file(audio_data, mimetype='audio/mpeg', as_attachment=True, download_name='audio.mp3')
    return render_template('home.html')


if __name__ == '__main__':
    app.run(debug=True)
