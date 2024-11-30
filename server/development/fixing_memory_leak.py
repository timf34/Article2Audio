import concurrent.futures
import logging
import gc

from io import BytesIO
from openai import OpenAI
from pydub import AudioSegment
from typing import List

from server.config import OPENAI_KEY

openai_client = OpenAI(api_key=OPENAI_KEY)
from memory_profiler import profile

with open("sample.txt", "r") as file:
    text = file.read()
    print(text)

@profile
def generate_audio_in_parallel(text: str) -> List:
    chunks = split_text_into_chunks(text, max_length=2048)
    audio_segments = [None] * len(chunks)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_index = {executor.submit(generate_audio_chunk, chunk, openai_client): i for i, chunk in enumerate(chunks)}
        for future in concurrent.futures.as_completed(future_to_index):
            index = future_to_index[future]
            try:
                audio_segments[index] = future.result()
            except Exception as e:
                logging.error(f"Failed to generate audio chunk at index {index}: {e}")
            finally:
                # Explicitly delete the future and enforce garbage collection
                del future
                gc.collect()  # Ensure garbage collection after each chunk

    return audio_segments


@profile
def generate_audio_chunk(chunk, openai_client) -> AudioSegment:
    response = openai_client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=chunk
    )
    audio_data = BytesIO(response.content)
    del response
    audio_segment = AudioSegment.from_file(audio_data, format="mp3")
    del audio_data
    gc.collect()
    print("Finished generating audio chunk")
    return audio_segment


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
