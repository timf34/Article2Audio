# Article2Audio

### Convert articles to audio using OpenAI's Text to Speech API, via a web app or simple python script.

Article2Audio is a straightforward web app designed for personal use, allowing users to convert online articles to 
lovely audio files. It extracts the content of an article, formats it nicely in preparation of audio conversion,
then uses OpenAI's Text to Speech API to produce the audio file. 

For ease of use, we also include a simple python script which allows users to directly convert article URLs to audio files
without needing to spin up the web app. 


### Sample Audio Output

[Sample Audio](https://github.com/timf34/Article2Audio/assets/66926418/bd6fb7e4-812d-455e-93df-1c12560eca13)

## Simple Python Script 

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/Article2Audio.git
   cd Article2Audio
   ```

2. **Add your openAI api key**
   
   Open `convert_article_urls_to_audio.py` and add your OpenAI API key to the `OPENAI_KEY` variable at the top of the file.

3. **Install the required packages:**
   ```bash
    pip install -r server/requirements.txt
    ```

### Usage

The script `convert_article_urls_to_audio.py` allows for two modes of operation:

1. **Default Mode**: By default it will use the URLs specified in the `HARDCODED_URLS` list at the top of the file.
   ```bash
   python convert_article_urls_to_audio.py
   ```
   
2. **Command Line Mode**: Overrides hardcoded URLs by specifying URLs via the command line with the --urls option.
   ```bash
   python convert_article_urls_to_audio.py --urls https://www.thefitzwilliam.com/p/james-joyce-was-a-complicated-man "https://www.honest-broker.com/p/how-picasso-turned-me-into-a-strategy"
   ```

##  Web App

###  Local Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/Article2Audio.git
   cd Article2Audio
   ```

2. **Create a `.env` file with necessary environment variables in the `/server` dir:**
    ```bash
    cd server   
    touch .env
    ```

    Add the following environment variables to the `.env` file:
   ```plaintext
   OPENAI_KEY=your-openai-key
   LOGIN_PASSWORD=your-password
   SECRET_KEY=your-secret-key
   ```

3. **Build and run Docker**
    ```bash
    docker compose up --build
    ```
   
Enjoy your audio versions of any article you want at http://localhost:3000! 🎉

Note that it can take up to a few minutes to generate the audio file depending on the length of the article. 
Will look into optimizing this/ running it concurrently without OpenAI rate limiting issues in the future. 
UI and iterface will be updated soon too, particularly with making the audio files
persist on the web interface so they're more readily available!
