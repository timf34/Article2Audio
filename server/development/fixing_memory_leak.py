import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import concurrent.futures
import logging
import gc

from io import BytesIO
from openai import OpenAI
from pydub import AudioSegment
from pydub.generators import WhiteNoise
from typing import List

OPENAI_KEY = "sk-proj-LSBB7YK5u2dPNatecXhuT3BlbkFJCeTbWMMUupZ08r2FLMfd"
openai_client = OpenAI(api_key=OPENAI_KEY)
from memory_profiler import profile

with open("development/sample.txt", "r") as file:
    print("current directory: ", os.getcwd())
    text = file.read()


@profile
def generate_audio_in_parallel(text: str) -> List:
    chunks = split_text_into_chunks(text, max_length=2048)
    print(f"Split text into {len(chunks)} chunks")
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
    # Simulate the response by creating a dummy audio segment
    response = create_audio_response_with_noise(duration=60000)

    # Export the audio to a BytesIO object
    audio_data = BytesIO()
    response.export(audio_data, format="mp3")
    audio_data.seek(0)

    # Calculate the size of the audio in the BytesIO object
    audio_size = len(audio_data.getvalue())
    print(f"Size of the resulting audio segment: {audio_size} bytes")
    print(f"Size of the resulting audio segment: {audio_size / 1024 / 1024} MB")

    # Convert the BytesIO content into an AudioSegment
    audio_segment = AudioSegment.from_file(audio_data, format="mp3")

    # Clean up
    del response
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


def create_audio_response_with_noise(duration=1000, noise_level: float = -30) -> AudioSegment:
    response = AudioSegment.silent(duration=duration)

    # Generate white noise with the specified duration and gain
    noise = WhiteNoise().to_audio_segment(duration=duration).apply_gain(noise_level)

    # Overlay noise onto the silent audio
    audio_with_noise = response.overlay(noise)
    return audio_with_noise


def main():
    # while True:
    #     input("Press Enter to generate audio segments")
    #     audio_segments = generate_audio_in_parallel(text)
    #     print(f"Generated {len(audio_segments)} audio segments")
    for i in range(5):
        audio_segments = generate_audio_in_parallel(text)
        print(f"Generated {len(audio_segments)} audio segments")


if __name__ == "__main__":
    main()
