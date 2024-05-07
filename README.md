# Article2Audio

**Convert articles to audio using OpenAI's Text to Speech API.**

Article2Audio is a straightforward web app designed for personal use, allowing users to convert online articles to 
lovely audio files. It extracts the content of an article, formats it nicely in preparation of audio conversion,
then uses OpenAI's Text to Speech API to produce the audio file. 

It has simple authentication to secure access and can be easily deployed on Vercel or run locally.

## Setup Instructions

### Local Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/Article2Audio.git
   cd Article2Audio
   ```

2. **Create a `.env` file with necessary environment variables:**
   ```plaintext
   OPENAI_KEY=your-openai-key
   LOGIN_PASSWORD=your-password
   SECRET_KEY=your-secret-key
   ```

3. **Install required packages:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python app.py
   ```

The app will be available at `http://localhost:5000`.

### Deployment on Vercel

1. **Fork or clone the repository to your GitHub account.**

2. **Connect your GitHub repository to Vercel:**
   - Go to [Vercel.com](https://vercel.com) and sign in.
   - Click on "New Project", find your repository, and select it.
   - Configure your project settings and specify the build commands and output directory if necessary.

3. **Add environment variables in Vercel:**
   - In your project settings on Vercel, navigate to the 'Environment Variables' section.
   - Add the following variables:
     - `OPENAI_KEY`: Your OpenAI API key.
     - `LOGIN_PASSWORD`: A password for login authentication.
     - `SECRET_KEY`: A secret key used for securely signing the session.

4. **Deploy the project:**
   - Vercel will automatically deploy your project when you push changes to your repository.
   - Access your project URL as provided by Vercel.