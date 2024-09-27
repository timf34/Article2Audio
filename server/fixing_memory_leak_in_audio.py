"""
This script is used to test the memory usage of the generate_audio_task function.
To simulate running in production, we'll keep this script running using a while loop, and have a key press to run again on the URL to generate audio.
And another key press to exit the loop.
"""
import tracemalloc
import psutil
from server.audio import generate_audio_task

PRACTICE_TEXT = """
The way to get new ideas is to notice anomalies: what seems strange, or missing, or broken? You can see anomalies in everyday life (much of standup comedy is based on this), but the best place to look for them is at the frontiers of knowledge.

Knowledge grows fractally. From a distance its edges look smooth, but when you learn enough to get close to one, you'll notice it's full of gaps. These gaps will seem obvious; it will seem inexplicable that no one has tried x or wondered about y. In the best case, exploring such gaps yields whole new fractal buds.

The way to get new ideas is to notice anomalies: what seems strange, or missing, or broken? You can see anomalies in everyday life (much of standup comedy is based on this), but the best place to look for them is at the frontiers of knowledge.

Knowledge grows fractally. From a distance its edges look smooth, but when you learn enough to get close to one, you'll notice it's full of gaps. These gaps will seem obvious; it will seem inexplicable that no one has tried x or wondered about y. In the best case, exploring such gaps yields whole new fractal buds.

The way to get new ideas is to notice anomalies: what seems strange, or missing, or broken? You can see anomalies in everyday life (much of standup comedy is based on this), but the best place to look for them is at the frontiers of knowledge.

Knowledge grows fractally. From a distance its edges look smooth, but when you learn enough to get close to one, you'll notice it's full of gaps. These gaps will seem obvious; it will seem inexplicable that no one has tried x or wondered about y. In the best case, exploring such gaps yields whole new fractal buds.
"""


def print_memory_usage():
    # Get current memory usage
    process = psutil.Process()
    memory_info = process.memory_info()
    print(f"Current memory usage: {memory_info.rss / (1024 * 1024):.2f} MB")


def main():
    while True:
        input("Press Enter to generate audio...")
        generate_audio_task(PRACTICE_TEXT, "test_article", "test_author", {}, "test_task_id")
        print("Processing complete. Checking memory usage...")
        print_memory_usage()


if __name__ == "__main__":
    main()


