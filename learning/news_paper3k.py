# from newspaper import Article
#
# url = 'http://fox13now.com/2013/12/30/new-year-new-laws-obamacare-pot-guns-and-drones/'
# article = Article(url)
#
# article.download()
# article.parse()
#
# print(article.text)

import requests
from newspaper import Config
from newspaper import fulltext

config = Config()
config.memoize_articles = False

# Replace 'your_article_url' with the actual URL of the article you want to fetch
url = 'https://www.newyorker.com/magazine/2024/05/06/the-battle-for-attention'
html = requests.get(url).text
print(html)
text = fulltext(html)

print(text)
