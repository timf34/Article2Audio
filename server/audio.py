import concurrent.futures
import logging
import os
import tempfile
import time

from io import BytesIO
from mutagen.easyid3 import EasyID3
from openai import OpenAI
from pathlib import Path
from pydub import AudioSegment
from typing import List, Dict

from config import MP3_DATA_DIR_PATH, DEVELOPMENT, OPENAI_KEY, S3_BUCKET_URL
from database import DatabaseManager
from rss_manager import update_rss_feed
from s3_manager import upload_file_to_s3
from utils import sanitize_filename

openai_client = OpenAI(api_key=OPENAI_KEY)
db_manager = DatabaseManager()


def generate_audio_task(text: str, article_name: str, author_name: str, tasks: Dict[str, str], task_id: str) -> None:
    try:
        if DEVELOPMENT:
            temp_file_path = "../speech.mp3"
        else:
            audio_segments = generate_audio_in_parallel(text)
            merged_audio = merge_audio_segments(audio_segments)

            print(f"article_name: {article_name}")
            print(f"author_name: {author_name}")
            print(f"tasks: {tasks}")
            print(f"task_id: {task_id}")

            save_path = save_audio_file(merged_audio, article_name, author_name)
            tasks[task_id] = {'status': 'completed', 'file_path': save_path, 'file_name': article_name}
            logging.info(f"Audio file saved in {save_path}")
    except Exception as e:
        logging.error(f"Failed to generate audio: {e}")
        tasks[task_id] = {'status': 'failed', 'detail': str(e)}


def create_audio_file(text: str, article_name: str, author_name: str) -> str:
    audio_segments = generate_audio_in_parallel(text)
    merged_audio = merge_audio_segments(audio_segments)
    file_path = save_audio_file(merged_audio, article_name, author_name)
    return file_path


def split_text_into_chunks(text, max_length=4096) -> List[str]:
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


def generate_audio_sequentially(text: str) -> List[AudioSegment]:
    chunks = split_text_into_chunks(text)
    audio_segments = []
    for chunk in chunks:
        response = openai_client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=chunk
        )
        audio_data = BytesIO(response.content)
        audio_segments.append(AudioSegment.from_file(audio_data, format="mp3"))
    print("finished generating audio segments")
    return audio_segments


def generate_audio_in_parallel(text: str) -> List[AudioSegment]:
    chunks = split_text_into_chunks(text, max_length=2048)   # TODO: be smarter about splitting the text, it affects the sound where its split, so should split at the end of a sentence or paragraph or such.
    audio_segments = [None] * len(chunks)
    print(audio_segments)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_index = {executor.submit(generate_audio_chunk, chunk, openai_client): i for i, chunk in enumerate(chunks)}
        for future in concurrent.futures.as_completed(future_to_index):
            index = future_to_index[future]
            try:
                audio_segments[index] = future.result()
            except Exception as e:
                logging.error(f"Failed to generate audio chunk at index {index}: {e}")
    return audio_segments


def generate_audio_chunk(chunk, openai_client) -> AudioSegment:
    response = openai_client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=chunk
    )
    audio_data = BytesIO(response.content)
    print("Finished generating audio chunk")
    return AudioSegment.from_file(audio_data, format="mp3")


def merge_audio_segments(audio_segments) -> AudioSegment:
    merged_audio = AudioSegment.empty()
    for segment in audio_segments:
        merged_audio += segment

    print("Finished merging audio segments")
    return merged_audio


def save_audio_to_temp_file(merged_audio: AudioSegment) -> str:
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
        merged_audio.export(temp_file.name, format="mp3")
        temp_file.seek(0)
        return temp_file.name


def save_audio_file(merged_audio: AudioSegment, article_name: str, author_name: str) -> str:
    try:
        output_dir = Path(MP3_DATA_DIR_PATH)
        if not output_dir.exists():
            logging.info(f"Creating directory: {output_dir}")
            output_dir.mkdir(parents=True, exist_ok=True)

        sanitized_title = sanitize_filename(article_name)
        sanitized_author = sanitize_filename(author_name)

        file_name = f"{sanitized_title} by {sanitized_author}.mp3"
        file_path = output_dir / file_name
        logging.info(f"About to save the audio file to {file_path}")
        merged_audio.export(file_path.as_posix(), format="mp3")
        logging.info(f"Audio file saved as {file_path}")

        # Add metadata using mutagen
        audio = EasyID3(file_path.as_posix())
        audio['title'] = sanitized_title
        audio['artist'] = author_name  # Use the original author name for metadata
        audio.save()

        # Check if it was saved successfully
        if not file_path.exists():
            raise ValueError("Failed to save the audio file.")

        db_manager.add_audio_file(file_name)

        if upload_file_to_s3(file_path.as_posix(), file_name):
            print(f"Successfully uploaded {file_name} to S3")

            file_url = f"{S3_BUCKET_URL}/{file_name.replace(' ', '%20')}"

            update_rss_feed(
                title=sanitized_title,
                author_name=author_name,
                description=f"Audio version of '{sanitized_title}' by {author_name}",
                file_url=file_url,
                file_size=str(os.path.getsize(file_path)),
                duration=str(merged_audio.duration_seconds)  # NOTE: I think this is supposed to be in H:MM:SS format
            )

        else:
            print(f"Failed to upload {file_name} to S3")

        return file_path.as_posix()
    except Exception as e:
        logging.error(f"Error in save_audio_file: {e}")
        raise


def time_audio_generation_per_character(client, text) -> float:
    start_time = time.time()
    audio_segments = generate_audio_sequentially(text)
    merged_audio = merge_audio_segments(audio_segments)
    end_time = time.time()

    generation_time = end_time - start_time
    average_time_per_character = generation_time / len(text)

    print(f"Total generation time: {generation_time:.2f} seconds")
    print(f"Average time per character: {average_time_per_character:.4f} seconds")

    return average_time_per_character