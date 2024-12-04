package article

import (
	goose "github.com/advancedlogic/GoOse"
)

type Article struct {
	goose *goose.Goose
}

func New() *Article {
	g := goose.New()
	return &Article{
		goose: &g,
	}
}

func (s *Article) ExtractContent(url string) (string, error) {
	article, err := s.goose.ExtractFromURL(url)
	if err != nil {
		return "", err
	}
	return article.CleanedText, nil
}
