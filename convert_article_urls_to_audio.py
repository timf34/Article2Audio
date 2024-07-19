"""
Including a simple script to directly convert a URL into an audio file rather than using the web app.
"""
import argparse
import os
import logging
import sys

from typing import List

sys.path.append(os.path.join(os.path.dirname(__file__), "./server"))  # For relative imports within /server scripts

from server.audio import create_audio_file
from server.readers import substack, articles
from server.utils import get_domain
from server.config import OPENAI_KEY  # Be sure to add a /server/.env file with the OPENAI_KEY var

if not OPENAI_KEY:
    raise EnvironmentError("OPENAI_KEY environment variable is not set. Please add it to your /server/.env file.")


# Hardcoded URLs - These will be used if no URLs are provided via command line
HARDCODED_URLS: List[str] = [
    # "https://gabiabrao.substack.com/p/how-to-make-love",
    "https://www.paulgraham.com/getideas.html"
]


def convert_url_to_audio_file(url: str) -> None:
    domain = get_domain(url)
    logging.info(f"Domain extracted: {domain}")

    try:
        if "substack.com" in domain:
            scraper = substack.SubstackScraper()
        else:
            scraper = articles.ArticleReader()

        text = scraper.get_post_content(url)
        article_name = scraper.get_article_name(url)
        author_name = scraper.get_author_name(url)
        del scraper

        if not text:
            raise ValueError("No content found at the provided URL.")

        file_path = create_audio_file(text, article_name, author_name, OPENAI_KEY)
        print(f"Audio file saved in {file_path}")
    except Exception as e:
        raise Exception(f"Error converting URL to audio: {e}") from e


def main():
    parser = argparse.ArgumentParser(description="Convert URLs to audio files.")
    parser.add_argument("--urls", nargs="*",
                        help="Optional: a list of URLs to convert to audio files. Overrides hardcoded URLs.")
    args = parser.parse_args()

    urls_to_process = args.urls if args.urls else HARDCODED_URLS

    for url in urls_to_process:
        convert_url_to_audio_file(url)


if __name__ == "__main__":
    main()
