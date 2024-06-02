"""
Given a url, produce a plain text file.

We won't include hyperlinks or images or any metadata.

It will be formatted as follows:

Title by Author

*pause*

Subtitle if there is one

*pause*

Content

TODO: I might want to either remove the footnotes, or integrate them into the text for audio reading.

"""
import re
from typing import Optional

from bs4 import BeautifulSoup
import html2text
import requests
from urllib.parse import urlparse

from readers.base_reader import BaseReader

URL: str = "https://www.experimental-history.com/p/so-you-wanna-de-bog-yourself"


def get_substack_name(url: str) -> str:
    parts = urlparse(url).netloc.split('.')  # Parse the URL to get the netloc, and split on '.'
    return parts[1] if parts[0] == 'www' else parts[0]  # Return the main part of the domain, while ignoring 'www' if


class SubstackScraper(BaseReader):
    def __init__(self):
        super().__init__()

        self.soup = None

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
        content = h.handle(html_content)

        content =  re.sub(r'^#+\s', '[pause]\n', content, flags=re.MULTILINE) # Remove the #'s, replacing them with single [pause]'s
        return re.sub(r'[_*]', '', content)  # Remove underscores and asterisks


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

    def extract_post_content(self, soup: BeautifulSoup, url: str) -> str:
        """
        Converts substack post soup to markdown, returns metadata and content
        """
        title = self.get_article_name(url)

        subtitle_element = soup.select_one("h3.subtitle")
        subtitle = subtitle_element.text.strip() if subtitle_element else ""

        author_name = self.get_author_name(url)

        content_div = soup.select_one("div.available-content")

        # Remove the subscription-widget-wrap div from the content
        subscription_widget = content_div.select_one("div.subscription-widget-wrap")
        if subscription_widget:
            subscription_widget.decompose()

        content = str(content_div)
        content = self.html_to_text(content)
        post_content = self.combine_metadata_and_content(title, author_name, subtitle, content)
        return post_content

    def get_post_content(self, url: str) -> str:

        if self.soup is None:
            self.soup = self.get_url_soup(url)

        # If the soup is still None, raise an error
        if self.soup is None:
            # TODO: raise an error
            raise ValueError("Error fetching page within substack.py")

        post_content = self.extract_post_content(self.soup, url)
        return post_content

    # Note: this and get_author_name don't seem the best designed... in that we have to pass the URL through more,
    #  but we can come back to this again.
    def get_article_name(self, url: str) -> str:
        if self.soup is None:
            self.soup = self.get_url_soup(url)

        # If the soup is still None, raise an error
        if self.soup is None:
            raise ValueError("Error fetching page within substack.py")

        # Article title
        # When a video is present, the title is demoted to h2
        return self.soup.select_one("h1.post-title, h2").text.strip()

    def get_author_name(self, url: str) -> Optional[str]:
        if self.soup is None:
            self.soup = self.get_url_soup(url)

        # If the soup is still None, raise an error
        if self.soup is None:
            raise ValueError("Error fetching page within substack.py")

        # Author name
        return self.soup.select_one("a._decoration-hover-underline_1k90y_298").text.strip()

    def save_post(self, url: str) -> None:
        """
        Saves the post to a file
        """
        post_content = self.get_post_content(url)
        filename = self.get_filename_from_url(url)
        self.save_to_file("output", post_content)
        print(f"Saved post: {filename}")

    @staticmethod
    def get_url_soup(url: str) -> Optional[BeautifulSoup]:
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
    scraper = SubstackScraper()
    print(scraper.get_post_content(URL))


if __name__ == "__main__":
    main()