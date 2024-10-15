"""
This script is used to test the memory usage of the generate_audio_task function.
To simulate running in production, we'll keep this script running using a while loop, and have a key press to run again on the URL to generate audio.
And another key press to exit the loop.
"""
import psutil
import uuid

from readers import substack, articles
from server.audio import generate_audio_task
from utils import get_domain


tasks = {}


def print_memory_usage():
    # Get current memory usage
    process = psutil.Process()
    memory_info = process.memory_info()
    print(f"Current memory usage: {memory_info.rss / (1024 * 1024):.2f} MB")


def main():

    while True:

        url = input("Enter URL to generate audio: ")

        domain = get_domain(url)

        if "substack.com" in domain:
            scraper = substack.SubstackScraper()
        else:
            scraper = articles.ArticleReader()

        task_id = str(uuid.uuid4())
        tasks[task_id] = {'status': 'scraping_url'}

        text = scraper.get_post_content(url)
        article_name = scraper.get_article_name(url)
        author_name = scraper.get_author_name(url)

        tasks[task_id] = {'status': 'Creating audio file...', 'article_name': article_name, 'author_name': author_name}

        generate_audio_task(text, article_name, author_name, tasks, task_id)
        print("Processing complete. Checking memory usage...")
        print_memory_usage()


if __name__ == "__main__":
    main()


