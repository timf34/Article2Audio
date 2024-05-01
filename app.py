from flask import Flask, render_template, request, redirect, url_for, send_file
from io import BytesIO
from openai import OpenAI
from config import OPENAI_KEY
from readers import substack

app = Flask(__name__)

client = OpenAI(api_key=OPENAI_KEY)

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
        # scraper = substack.SubstackScraper()
        # text = scraper.get_post_content(url)
        text = "what can we expect from friendship? \
                    [pause]\
                    I will arise and go now, and go to inisfree"
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text
        )
        audio_data = BytesIO(response.content)
        # with open("speech.mp3", "rb") as file:
        #     audio_data = file.read()
        return send_file(audio_data, mimetype='audio/mpeg', as_attachment=True, download_name='audio.mp3')
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True)