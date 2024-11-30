import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import concurrent.futures
import logging
import gc
# gc.set_debug(gc.DEBUG_LEAK)
import time

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

import concurrent.futures
import logging
import gc
import weakref

from io import BytesIO
from openai import OpenAI
from pydub import AudioSegment
from pydub.generators import WhiteNoise
from typing import List
from contextlib import contextmanager

import concurrent.futures
import logging
import gc
import weakref

from io import BytesIO
from openai import OpenAI
from pydub import AudioSegment
from pydub.generators import WhiteNoise
from typing import List
from contextlib import contextmanager


@contextmanager
def cleanup_resources():
    """Context manager to ensure proper cleanup of resources"""
    try:
        yield
    finally:
        gc.collect()


@profile
def generate_audio_in_parallel(text: str) -> List:
    chunks = 3
    print(f"Split text into {len(chunks)} chunks")
    audio_segments = []

    with cleanup_resources(), concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = []
        # Submit all tasks
        for chunk in chunks:
            future = executor.submit(generate_audio_chunk, chunk, openai_client)
            futures.append(future)

        # Process results as they complete
        for future in concurrent.futures.as_completed(futures):
            try:
                segment = future.result()
                if segment:
                    audio_segments.append(segment)
            except Exception as e:
                logging.error(f"Failed to generate audio chunk: {e}")
            finally:
                # Ensure future is done and its resources are released
                if not future.done():
                    future.cancel()
                del future

    return audio_segments


@profile
def generate_audio_chunk(chunk, openai_client) -> AudioSegment:
    with cleanup_resources():
        try:
            # Simulate the response by creating a dummy audio segment
            response = create_audio_response_with_noise(duration=60000)

            # Export the audio to a BytesIO object using context manager
            with BytesIO() as audio_data:
                response.export(audio_data, format="mp3")
                audio_data.seek(0)

                # Calculate the size of the audio in the BytesIO object
                audio_size = len(audio_data.getvalue())
                print(f"Size of the resulting audio segment: {audio_size} bytes")
                print(f"Size of the resulting audio segment: {audio_size / 1024 / 1024} MB")

                # Convert the BytesIO content into an AudioSegment
                audio_segment = AudioSegment.from_file(audio_data, format="mp3")

                # Create a copy of the audio data
                final_segment = AudioSegment(
                    audio_segment._data,
                    frame_rate=audio_segment.frame_rate,
                    sample_width=audio_segment.sample_width,
                    channels=audio_segment.channels
                )

                return final_segment

        finally:
            # # Explicit cleanup of large objects
            # if 'response' in locals():
            #     del response
            # if 'audio_segment' in locals():
            #     del audio_segment
            gc.collect()
            print("Finished generating audio chunk")


def create_audio_response_with_noise(duration=1000, noise_level: float = -30) -> AudioSegment:
    with cleanup_resources():
        response = AudioSegment.silent(duration=duration)
        noise = WhiteNoise().to_audio_segment(duration=duration).apply_gain(noise_level)
        audio_with_noise = response.overlay(noise)

        # Clean up intermediate objects
        del response
        del noise

        return audio_with_noise

def main():
    # while True:
    #     input("Press Enter to generate audio segments")
    #     audio_segments = generate_audio_in_parallel(text)
    #     print(f"Generated {len(audio_segments)} audio segments")
    # print("Consumed memory at start: ", gc.get_objects())
    for i in range(5):
        audio_segments = generate_audio_in_parallel(text)
        print(f"Generated {len(audio_segments)} audio segments")
        del audio_segments
        gc.collect()

    time.sleep(10)


if __name__ == "__main__":
    main()
