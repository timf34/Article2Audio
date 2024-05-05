"""
Base Reader to inherit from

Given a URL the subclasses should return a string with the content of the article in the structure:

{Title} by {Author}

[pause]

{Post Content}
"""

from abc import ABC, abstractmethod
from typing import Optional
import os


class BaseReader:
    def __init__(self):
        pass

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
    def combine_metadata_and_content(title: str, author_name: Optional[str], subtitle: Optional[str], content: str) -> str:
        """
        Combines the title, subtitle, and content into a single string with Markdown format
        """
        if not isinstance(title, str):
            raise ValueError("title must be a string")

        if not isinstance(content, str):
            raise ValueError("content must be a string")

        metadata = f"{title}"

        if author_name:
            metadata += f" by {author_name}"

        metadata += "\n [pause] \n"

        if subtitle:
            metadata += f"{subtitle}\n\n"
            metadata += "\n [pause] \n"

        return metadata + content

    def get_post_content(self, url: str) -> str:
        """
        Given a URL, returns the content of the post
        """
        raise NotImplementedError("Subclasses must implement this method")