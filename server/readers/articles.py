import newspaper

from typing import Optional

from readers.base_reader import BaseReader


class ArticleReader(BaseReader):
    def __init__(self):
        super().__init__()
        self.article = None

    def get_post_content(self, url: str) -> str:
        if self.article is None:
            self.article = newspaper.article(url)
        title = self.article.title
        author = self.article.authors[0] if len(self.article.authors) > 0 else None
        content = self.article.text
        return self.combine_metadata_and_content(title, author, None, content)

    def get_article_name(self, url: str) -> str:
        if self.article is None:
            self.article = newspaper.article(url)
        return self.article.title

    def get_author_name(self, url: str) -> Optional[str]:
        if self.article is None:
            self.article = newspaper.article(url)
        return self.article.authors[0] if len(self.article.authors) > 0 else None
