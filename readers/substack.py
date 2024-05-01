"""
Given a url, produce a plain text file.

We won't include hyperlinks or images or any metadata.

It will be formatted as follows:

Title by Author

*pause*

Subtitle if there is one

*pause*

Content

"""

import os
import re
from abc import ABC, abstractmethod
from typing import Optional

from bs4 import BeautifulSoup
import html2text
import requests
from xml.etree import ElementTree as ET
from urllib.parse import urlparse

URL: str = "https://www.experimental-history.com/p/so-you-wanna-de-bog-yourself"


def get_substack_name(url: str) -> str:
    parts = urlparse(url).netloc.split('.')  # Parse the URL to get the netloc, and split on '.'
    return parts[1] if parts[0] == 'www' else parts[0]  # Return the main part of the domain, while ignoring 'www' if


class BaseSubstackScraper(ABC):
    def __init__(self, base_substack_url: str):
        if not base_substack_url.endswith("/"):
            base_substack_url += "/"
        self.base_substack_url: str = base_substack_url

        self.writer_name: str = get_substack_name(base_substack_url)

    @staticmethod
    def html_to_text(html_content: str) -> str:
        """
        This method converts HTML to Markdown
        """
        if not isinstance(html_content, str):
            raise ValueError("html_content must be a string")
        h = html2text.HTML2Text()
        h.ignore_links = True
        h.ignore_images = True
        h.body_width = 0
        h.ignore_tables = True
        # TODO: this converts it to markdown, but we need to remove the #'s and replace them with [pause]. Might be cleaner if there's a way to just convert to text while only keeping the main text content
        content =  h.handle(html_content)

        content =  re.sub(r'^#+\s', '[pause]\n', content, flags=re.MULTILINE) # Remove the #'s, replacing them with single [pause]'s
        return re.sub(r'[_*]', '', content)  # Remove underscores and asterisks


    @staticmethod
    def save_to_file(filepath: str, content: str) -> None:
        """
        This method saves content to a file. Can be used to save HTML or Markdown
        """
        if not isinstance(filepath, str):
            raise ValueError("filepath must be a string")

        if not isinstance(content, str):
            raise ValueError("content must be a string")

        if os.path.exists(filepath):
            print(f"File already exists: {filepath}")
            return

        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(content)

    @staticmethod
    def get_filename_from_url(url: str, filetype: str = ".md") -> str:
        """
        Gets the filename from the URL (the ending)
        """
        if not isinstance(url, str):
            raise ValueError("url must be a string")

        if not isinstance(filetype, str):
            raise ValueError("filetype must be a string")

        if not filetype.startswith("."):
            filetype = f".{filetype}"

        return url.split("/")[-1] + filetype

    @staticmethod
    def combine_metadata_and_content(title: str, author_name: str, subtitle: str, content: str) -> str:
        """
        Combines the title, subtitle, and content into a single string with Markdown format
        """
        if not isinstance(title, str):
            raise ValueError("title must be a string")

        if not isinstance(content, str):
            raise ValueError("content must be a string")

        metadata = f"{title} by {author_name}\n\n"

        metadata += "\n [pause] \n"

        if subtitle:
            metadata += f"{subtitle}\n\n"
            metadata += "\n [pause] \n"

        return metadata + content

    def extract_post_content(self, soup: BeautifulSoup) -> str:
        """
        Converts substack post soup to markdown, returns metadata and content
        """
        title = soup.select_one("h1.post-title, h2").text.strip()  # When a video is present, the title is demoted to h2

        subtitle_element = soup.select_one("h3.subtitle")
        subtitle = subtitle_element.text.strip() if subtitle_element else ""

        author_name = soup.select_one("div.profile-hover-card-target").text.strip()

        content_div = soup.select_one("div.available-content")

        # Remove the subscription-widget-wrap div from the content
        subscription_widget = content_div.select_one("div.subscription-widget-wrap")
        if subscription_widget:
            subscription_widget.decompose()

        content = str(content_div)
        content = self.html_to_text(content)
        post_content = self.combine_metadata_and_content(title, author_name, subtitle, content)
        return post_content

    def save_post(self, url: str) -> None:
        """
        Saves the post to a file
        """
        soup = self.get_url_soup(url)
        if soup is None:
            return

        post_content = self.extract_post_content(soup)
        filename = self.get_filename_from_url(url)
        self.save_to_file("output", post_content)
        print(f"Saved post: {filename}")

    @abstractmethod
    def get_url_soup(self, url: str) -> str:
        raise NotImplementedError


class SubstackScraper(BaseSubstackScraper):
    def __init__(self, base_substack_url: str):
        super().__init__(base_substack_url)

    def get_url_soup(self, url: str) -> Optional[BeautifulSoup]:
        """
        Gets soup from URL using requests
        """
        try:
            page = requests.get(url, headers=None)
            soup = BeautifulSoup(page.content, "html.parser")
            if soup.find("h2", class_="paywall-title"):
                print(f"Skipping premium article: {url}")
                return None
            return soup
        except Exception as e:
            raise ValueError(f"Error fetching page: {e}") from e


def main():
    scraper = SubstackScraper(URL)
    scraper.save_post(URL)


if __name__ == "__main__":
    main()