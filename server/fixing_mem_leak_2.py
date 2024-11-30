import numpy as np
import concurrent.futures
import gc
import logging
from typing import List
import psutil
import time
import threading


# Simulates tensor generation instead of TTS
def generate_tensor_chunk(chunk: str, tensor_size_mb: int = 100) -> np.ndarray:
    """Simulate tensor creation for memory-intensive operation."""
    size_in_bytes = tensor_size_mb * 1024 * 1024
    tensor = np.zeros((size_in_bytes // 8,), dtype=np.float64)
    return tensor


def split_text_into_chunks(text: str, max_length: int) -> List[str]:
    """Splits text into chunks of max_length."""
    return [text[i:i + max_length] for i in range(0, len(text), max_length)]


def generate_audio_in_parallel(text: str) -> List[np.ndarray]:
    """Simulates the generation of large tensors in parallel."""
    chunks = split_text_into_chunks(text, max_length=2048)
    tensors = [None] * len(chunks)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_index = {
            executor.submit(generate_tensor_chunk, chunk): i for i, chunk in enumerate(chunks)
        }
        for future in concurrent.futures.as_completed(future_to_index):
            index = future_to_index[future]
            try:
                tensors[index] = future.result()
            except Exception as e:
                logging.error(f"Failed to generate tensor chunk at index {index}: {e}")
            finally:
                # Explicitly delete the future and enforce garbage collection
                del future
                gc.collect()  # Force garbage collection to simulate cleanup

    return tensors


# Memory monitoring function
def monitor_memory(interval=2):
    """Periodically print memory usage."""
    process = psutil.Process()
    while True:
        memory_info = process.memory_info()
        print(f"Memory Usage: {memory_info.rss / (1024 * 1024):.2f} MB")
        time.sleep(interval)


# Main function simulating a long-running server
def main():
    # Start memory monitoring in a separate thread
    monitor_thread = threading.Thread(target=monitor_memory, args=(2,), daemon=True)
    monitor_thread.start()

    test_text = "This is a test string. " * 10000  # Simulate large input

    while True:
        input("Press Enter to run the generate_audio_in_parallel function...")

        print("Memory usage before running function:")
        memory_info_before = psutil.Process().memory_info()
        print(f"  RSS: {memory_info_before.rss / (1024 * 1024):.2f} MB")

        tensors = generate_audio_in_parallel(test_text)
        print(f"Generated {len(tensors)} tensor chunks.")

        print("Memory usage after running function:")
        memory_info_after = psutil.Process().memory_info()
        print(f"  RSS: {memory_info_after.rss / (1024 * 1024):.2f} MB")

        print("Press Enter to run the function again or Ctrl+C to exit.")


if __name__ == "__main__":
    main()
