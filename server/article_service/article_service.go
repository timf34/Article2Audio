package main

import (
	goose "github.com/advancedlogic/GoOse"
)

type ArticleService struct {
	goose *goose.Goose
}

func NewArticleService() *ArticleService {
	g := goose.New()
	return &ArticleService{
		goose: &g,
	}
}

func (s *ArticleService) ExtractContent(url string) (string, error) {
	article, err := s.goose.ExtractFromURL(url)
	if err != nil {
		return "", err
	}
	return article.CleanedText, nil
}
