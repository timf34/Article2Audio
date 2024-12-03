import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import concurrent.futures
import logging
import os
import gc
import psutil
# gc.set_debug(gc.DEBUG_LEAK)
import time

from contextlib import contextmanager
from datetime import datetime
from io import BytesIO
from openai import OpenAI
from pydub import AudioSegment
from pydub.generators import WhiteNoise
from typing import List

OPENAI_KEY = "sk-proj-LSBB7YK5u2dPNatecXhuT3BlbkFJCeTbWMMUupZ08r2FLMfd"
openai_client = OpenAI(api_key=OPENAI_KEY)
from memory_profiler import profile
from audio import split_text_into_chunks

with open("sample.txt", "r") as file:
    print("current directory: ", os.getcwd())
    text = file.read()


USE_REAL_TTS = True


class MemoryMonitor:
    def __init__(self, logging_interval=1):
        self.process = psutil.Process()
        self.logging_interval = logging_interval
        self.start_time = time.time()
        self.base_memory = self.get_memory_usage()
        self.log_file = f"memory_usage_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        # Initialize log file with headers
        with open(self.log_file, 'w') as f:
            f.write("timestamp,elapsed_time,rss_memory_mb,virtual_memory_mb,memory_percent\n")

    def get_memory_usage(self):
        """Get current memory usage in MB"""
        self.process.memory_info()  # Update memory info
        return {
            'rss': self.process.memory_info().rss / (1024 * 1024),  # RSS in MB
            'vms': self.process.memory_info().vms / (1024 * 1024),  # Virtual memory in MB
            'percent': self.process.memory_percent()
        }

    def log_memory(self):
        """Log current memory usage to file"""
        memory = self.get_memory_usage()
        elapsed_time = time.time() - self.start_time

        with open(self.log_file, 'a') as f:
            f.write(f"{datetime.now().isoformat()},{elapsed_time:.2f},"
                    f"{memory['rss']:.2f},{memory['vms']:.2f},{memory['percent']:.2f}\n")

        print(f"Memory Usage - RSS: {memory['rss']:.2f}MB, "
              f"Virtual: {memory['vms']:.2f}MB, "
              f"Percent: {memory['percent']:.2f}%")


@contextmanager
def cleanup_resources():
    """Context manager to ensure proper cleanup of resources"""
    try:
        yield
    finally:
        gc.collect()


@profile
def generate_audio_in_parallel(text: str, memory_monitor: MemoryMonitor) -> List:
    if USE_REAL_TTS:
        chunks = split_text_into_chunks(text, max_length=2048)
    else:
        chunks = [1, 2, 3]  # Fixed list instead of integer

    print(f"Split text into {len(chunks)} chunks")
    audio_segments = []

    with cleanup_resources(), concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for chunk in chunks:
            future = executor.submit(generate_audio_chunk, chunk, openai_client)
            futures.append(future)

        for future in concurrent.futures.as_completed(futures):
            try:
                segment = future.result()
                if segment:
                    audio_segments.append(segment)
                memory_monitor.log_memory()  # Log memory after each chunk
            except Exception as e:
                logging.error(f"Failed to generate audio chunk: {e}")
            finally:
                if not future.done():
                    future.cancel()
                del future

    return audio_segments


@profile
def generate_audio_chunk(chunk, openai_client) -> AudioSegment:
    """
    Generate an audio segment for a given text chunk.
    Uses either the real TTS API or a simulated resource-intensive operation based on the USE_REAL_TTS flag.
    """
    with cleanup_resources():
        try:
            if USE_REAL_TTS:
                # Use the real TTS API
                print("Using the real TTS API")
                response = openai_client.audio.speech.create(
                    model="tts-1",
                    voice="alloy",
                    input=chunk
                )
                # Real API response, convert content to a BytesIO object
                audio_data = BytesIO(response.content)
            else:
                # Simulate memory-intensive operation
                print("Simulating memory usage instead of TTS API")
                simulated_audio = simulate_memory_usage(size_mb=50)  # Simulated AudioSegment
                # Convert AudioSegment to a BytesIO object for compatibility
                audio_data = BytesIO()
                simulated_audio.export(audio_data, format="mp3")
                audio_data.seek(0)

            # Create AudioSegment from the BytesIO object
            audio_segment = AudioSegment.from_file(audio_data, format="mp3")

            audio_size = len(audio_segment._data)
            print(f"Size of the resulting audio segment: {audio_size / 1024 / 1024} MB")

            return audio_segment
        finally:
            gc.collect()
            print("Finished generating audio chunk")


def simulate_memory_usage(size_mb: int) -> AudioSegment:
    """
    Simulate a resource-intensive operation by creating a large in-memory object
    and embedding it into an audio-like format.
    """
    print(f"Simulating {size_mb} MB memory usage")

    # Create a repeating pattern efficiently and scale it to the desired size
    pattern = bytes(range(256))  # 256 unique bytes (0 to 255)
    data = pattern * (size_mb * 1024 * 1024 // len(pattern))  # Repeat to fill desired size
    data += pattern[: (size_mb * 1024 * 1024 % len(pattern))]  # Add remaining bytes if needed

    # Use the byte array as raw audio data to create an AudioSegment
    response = AudioSegment(
        data=bytes(data),  # Use the large byte array as the "audio data"
        sample_width=2,  # 16-bit audio
        frame_rate=44100,  # Standard audio sample rate
        channels=1  # Mono audio
    )

    print(f"Simulated audio segment created with size: {len(data) / (1024 * 1024):.2f} MB")

    return response


def create_audio_response_with_noise(duration=1000, noise_level: float = -30) -> AudioSegment:
    with cleanup_resources():
        response = AudioSegment.silent(duration=duration)
        noise = WhiteNoise().to_audio_segment(duration=duration).apply_gain(noise_level)
        audio_with_noise = response.overlay(noise)
        return audio_with_noise


def main():
    # Initialize memory monitor
    memory_monitor = MemoryMonitor(logging_interval=1)
    print(f"Starting memory usage: {memory_monitor.base_memory['rss']:.2f} MB")

    try:
        for i in range(1):
            print(f"\nIteration {i + 1}/5")
            audio_segments = generate_audio_in_parallel(text, memory_monitor)
            print(f"Generated {len(audio_segments)} audio segments")
            del audio_segments
            gc.collect()
            memory_monitor.log_memory()
            time.sleep(2)  # Short pause between iterations

        print("\nFinal memory check after 10 seconds...")
        time.sleep(10)
        memory_monitor.log_memory()

    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")
    finally:
        print(f"\nMemory usage log saved to: {memory_monitor.log_file}")


if __name__ == "__main__":
    main()
