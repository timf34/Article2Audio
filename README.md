# Article2Audio

 _Not in a useable state right now! Will be soon, and easy to self-host, etc.!_

**Convert articles to audio using OpenAI's Text to Speech API.**

Article2Audio is a straightforward web app designed for personal use, allowing users to convert online articles to 
lovely audio files. It extracts the content of an article, formats it nicely in preparation of audio conversion,
then uses OpenAI's Text to Speech API to produce the audio file. 


### Sample Audio Output

<audio controls>
  <source src="server/data/output/The%20Most%20Precious%20Resource%20is%20Agency.mp3" type="audio/mpeg">
  Your browser does not support the audio element.
</audio>

## Setup Instructions

### Local Setup

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
    docker-compose up --build
    ```
   
Enjoy your audio versions of any article you want! 🎉

Note that it can take up to a few minutes to generate the audio file depending on the length of the article. 
Will look into optimizing this/ running it concurrently without OpenAI rate limiting issues in the future. 
UI and iterface will be updated soon too!
