from datetime import datetime
import logging

import os
import tempfile
import time

from io import BytesIO
from openai import OpenAI
from pathlib import Path
from pydub import AudioSegment
from typing import List, Dict

from config import AUDIO_FILE_NAME, DEVELOPMENT, LAST_MODIFIED_FILE_NAME, OPENAI_KEY

openai_client = OpenAI(api_key=OPENAI_KEY)


def generate_audio_task(text: str, tasks: Dict[str, str], task_id: str) -> None:
    try:
        if DEVELOPMENT:
            temp_file_path = "../speech.mp3"
        else:
            audio_segments = generate_audio(text)
            merged_audio = merge_audio_segments(audio_segments)
            save_path = save_audio_file(merged_audio, task_id)
            tasks[task_id] = {'status': 'completed', 'file_path': save_path}
            logging.info(f"Audio file saved in {save_path}")
    except Exception as e:
        logging.error(f"Failed to generate audio: {e}")
        tasks[task_id] = {'status': 'failed', 'detail': str(e)}

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


def generate_audio(text) -> List[AudioSegment]:
    print("before split_text_into_chunks")
    chunks = split_text_into_chunks(text)
    print("after split_text_into_chunks")
    audio_segments = []
    for chunk in chunks:
        print("before client.audio.speech.create")
        # time.sleep(10)
        response = openai_client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=chunk
        )
        audio_data = BytesIO(response.content)
        audio_segments.append(AudioSegment.from_file(audio_data, format="mp3"))
    print("finished generating audio segments")
    return audio_segments


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


def save_audio_file(merged_audio: AudioSegment, task_id: str) -> str:
    try:
        output_dir = Path("data/output/")
        if not output_dir.exists():
            logging.info(f"Creating directory: {output_dir}")
            output_dir.mkdir(parents=True, exist_ok=True)

        file_path = output_dir / f"{task_id}.mp3"
        logging.info(f"About to save the audio file to {file_path}")
        merged_audio.export(file_path.as_posix(), format="mp3")
        logging.info(f"Audio file saved as {file_path}")

        # Check if it was saved successfully
        if not file_path.exists():
            raise ValueError("Failed to save the audio file.")

        return file_path.as_posix()
    except Exception as e:
        logging.error(f"Error in save_audio_file: {e}")
        raise


def time_audio_generation_per_character(client, text) -> float:
    start_time = time.time()
    audio_segments = generate_audio(client, text)
    merged_audio = merge_audio_segments(audio_segments)
    end_time = time.time()

    generation_time = end_time - start_time
    average_time_per_character = generation_time / len(text)

    print(f"Total generation time: {generation_time:.2f} seconds")
    print(f"Average time per character: {average_time_per_character:.4f} seconds")

    return average_time_per_character