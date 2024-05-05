import newspaper

# article = newspaper.article('https://www.newyorker.com/magazine/2024/05/06/the-battle-for-attention')  # Works
# article = newspaper.article('https://www.theatlantic.com/technology/archive/2024/05/boston-dynamics-robot-videos-youtube/678261/')  # Works
article = newspaper.article('https://www.newyorker.com/culture/the-weekend-essay/the-hidden-pregnancy-experiment')
# article = newspaper.article('https://archive.is/cdyCT')  # Doesn't work, but note that the scraper works at getting the full content so we don't need to use archive


print(article.text)
print(article.authors)
print(article.title)
