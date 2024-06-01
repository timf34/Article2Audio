from datetime import datetime
import logging

import os
import tempfile
import time

from io import BytesIO
from openai import OpenAI
from pydub import AudioSegment
from typing import List, Dict

from config import AUDIO_FILE_NAME, DEVELOPMENT, LAST_MODIFIED_FILE_NAME, OPENAI_KEY

openai_client = OpenAI(api_key=OPENAI_KEY)


# Temp
def generate_audio_task(text: str, tasks: Dict[str, str], task_id: str) -> None:
    print("in generate_audio_task")

    if DEVELOPMENT:
        temp_file_path = "../speech.mp3"
    else:
        print("before generate audio")
        audio_segments = generate_audio(text)
        print("after generate audio")
        merged_audio = merge_audio_segments(audio_segments)
        print("after merge audio")
        with open(LAST_MODIFIED_FILE_NAME, 'w') as file:
            file.write(datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
        print("after write last modified")
        save_audio_file(merged_audio)
        tasks[task_id] = {'status': 'complete'}
        print("after save audio file")

        # Get current working directory
        pwd = os.getcwd()
        print(f"Audio file saved in {pwd} as {AUDIO_FILE_NAME}")
        logging.info(f"Audio file saved in {pwd} as {AUDIO_FILE_NAME}")


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


def save_audio_file(merged_audio: AudioSegment) -> None:
    print("About to save the audio file")
    merged_audio.export(AUDIO_FILE_NAME, format="mp3")
    print(f"Audio file saved as {AUDIO_FILE_NAME}")
    # Check if it was saved successfully
    if not os.path.exists(AUDIO_FILE_NAME):
        raise ValueError("Failed to save the audio file.")


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