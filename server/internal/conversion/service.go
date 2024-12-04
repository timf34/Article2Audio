package conversion

import (
	"article2audio/internal/storage"
	"sync"

	"article2audio/internal/article"
	"article2audio/internal/audio"
)

type AudioConverter struct {
	jobs          map[string]*ConversionJob
	mu            sync.RWMutex
	storage       *storage.S3Storage
	audioGen      *audio.Audio
	articleParser *article.Article
}

func New(
	storage *storage.S3Storage,
	audioGen *audio.Audio,
	articleParser *article.Article,
) *AudioConverter {
	return &AudioConverter{
		jobs:          make(map[string]*ConversionJob),
		storage:       storage,
		audioGen:      audioGen,
		articleParser: articleParser,
	}
}
