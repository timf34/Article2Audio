"""
Test that the scraper works well for a few different domains.

In case it doesn't find the author or article name, it should return "unknonwn".
"""
import pytest
import sys
from unittest.mock import patch, MagicMock
from typing import List

sys.path.append("../server")
from readers import substack, articles

# Collection of official news sites, substacks, and personal blogs
# TODO: find shorter blog posts
URLS: List[str] = [
    "https://www.paulgraham.com/getideas.html",
    "https://www.avabear.xyz/p/written-in-the-body",
    "https://www.theatlantic.com/ideas/archive/2024/07/microsoft-outage-technological-systems-fail/679110/",
    "https://www.newyorker.com/tech/annals-of-technology/the-first-light-of-the-trinity-atomic-test",
    "https://jsomers.net/blog/speed-matters",
    "https://www.benkuhn.net/conviction/",
    "https://map.simonsarris.com/p/the-most-precious-resource-is-agency",
    "https://gabiabrao.substack.com/p/how-to-read"
]


@pytest.fixture
def mock_substack_scraper():
    with patch('server.readers.substack.SubstackScraper') as MockClass:
        instance = MockClass.return_value
        instance.get_post_content.return_value = "Sample content"
        instance.get_article_name.return_value = "Sample article"
        instance.get_author_name.return_value = "Sample author"
        yield instance


@pytest.fixture
def mock_article_reader():
    with patch('server.readers.articles.ArticleReader') as MockClass:
        instance = MockClass.return_value
        instance.get_post_content.return_value = "Sample content"
        instance.get_article_name.return_value = "Sample article"
        instance.get_author_name.return_value = "Sample author"
        yield instance


@pytest.mark.parametrize("url", URLS)
def test_scraper(mock_substack_scraper, mock_article_reader, url):
    domain = url.split('/')[2]

    if "substack.com" in domain:
        scraper = substack.SubstackScraper()
    else:
        scraper = articles.ArticleReader()

    text = scraper.get_post_content(url)
    article_name = scraper.get_article_name(url)
    author_name = scraper.get_author_name(url)

    word_count = len(text.split())
    print(f"URL: {url}")
    print(f"Number of words in content: {word_count}")
    print(f"Article name: {article_name}")
    print(f"Author name: {author_name}\n")

    # Assertions
    assert text is not None and text != "", "Text content should not be None or empty"
    assert article_name is not None and article_name != "", "Article name should not be None or empty"
    assert author_name is not None and author_name != "", "Author name should not be None or empty"



