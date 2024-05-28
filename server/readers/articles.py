import newspaper

from readers.base_reader import BaseReader


class ArticleReader(BaseReader):
    def __init__(self):
        super().__init__()

    def get_post_content(self, url: str) -> str:
        article = newspaper.article(url)
        title = article.title
        author = article.authors[0] if len(article.authors) > 0 else None
        content = article.text
        return self.combine_metadata_and_content(title, author, None, content)
