"""
Including a simple script to directly convert a URL into an audio file rather than using the web app.
"""
import os
import uuid
import logging
import sys

from typing import List

# Append the server directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), "./server"))

from server.models import URLRequest
from server.audio import create_audio_file
from server.readers import substack, articles
from server.utils import get_domain

# TODO: Need to add a way for users to add their openai key here


def convert_url_to_audio_file(url: str) -> None:
    domain = get_domain(url)
    logging.info(f"Domain extracted: {domain}")

    try:
        if "substack.com" in domain:
            # TODO: need to recognize custom substack domains
            scraper = substack.SubstackScraper()
        else:
            scraper = articles.ArticleReader()

        text = scraper.get_post_content(url)
        article_name = scraper.get_article_name(url)
        author_name = scraper.get_author_name(url)
        del scraper

        if not text:
            raise ValueError("No content found at the provided URL.")

        file_path = create_audio_file(text, article_name, author_name)
        print(f"Audio file saved in {file_path}")
    except Exception as e:
        raise ValueError(f"Error processing article: {e}")


def main():
    urls: List[str] = [
        "https://gabiabrao.substack.com/p/how-to-make-love",
    ]

    for url in urls:
        logging.info(f"Processing URL: {url}")
        convert_url_to_audio_file(url)


if __name__ == "__main__":
    main()
