"""
This script is used to test the memory usage of the generate_audio_task function.
To simulate running in production, we'll keep this script running using a while loop, and have a key press to run again on the URL to generate audio.
And another key press to exit the loop.
"""
import tracemalloc
import psutil
from server.audio import generate_audio_task

PRACTICE_URL = "https://www.paulgraham.com/getideas.html"


def print_memory_usage():
    # Get current memory usage
    process = psutil.Process()
    memory_info = process.memory_info()
    print(f"Current memory usage: {memory_info.rss / (1024 * 1024):.2f} MB")

    # Get memory usage from tracemalloc
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')
    print("\nTop 10 memory allocations:")
    for stat in top_stats[:10]:
        print(stat)


def main():
    while True:
        input("Press Enter to generate audio...")
        generate_audio_task(PRACTICE_URL, "test_article", "test_author", {}, "test_task_id")
        print("Processing complete. Checking memory usage...")
        print_memory_usage()


if __name__ == "__main__":
    main()


