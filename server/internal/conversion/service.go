package conversion

import (
	"article2audio/internal/article"
	"article2audio/internal/audio"
	"article2audio/internal/rss"
	"article2audio/internal/storage"
	"fmt"
	"github.com/google/uuid"
	"log"
	"sync"
)

type AudioConverter struct {
	jobs          map[string]*ConversionJob
	mu            sync.RWMutex
	storage       *storage.S3Storage
	audioGen      *audio.Audio
	articleParser *article.Article
	rssService    *rss.RSSService
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
		rssService:    rss.New(storage),
	}
}

func (ac *AudioConverter) StartConversion(userID, url string) (*ConversionJob, error) {
	jobID := uuid.New().String()

	job := &ConversionJob{
		ID:     jobID,
		URL:    url,
		Status: StatusPending,
		UserID: userID,
	}

	ac.mu.Lock()
	ac.jobs[jobID] = job
	ac.mu.Unlock()

	// Start processing in the background
	go ac.processJob(userID, job)

	return job, nil
}

// GetStatus returns the current status of a conversion job
func (ac *AudioConverter) GetStatus(jobID string) (*ConversionJob, error) {
	ac.mu.RLock()
	defer ac.mu.RUnlock()

	job, exists := ac.jobs[jobID]
	if !exists {
		return nil, fmt.Errorf("job not found")
	}

	return job, nil
}

func (ac *AudioConverter) ListAudioFiles(userID string) ([]storage.AudioFile, error) {
	return ac.storage.ListAudioFiles(userID)
}

func (ac *AudioConverter) processJob(userID string, job *ConversionJob) {
	ac.updateJobStatus(job, StatusParsing)

	// Extract article content
	content, err := ac.articleParser.ExtractContent(job.URL)
	if err != nil {
		ac.handleJobError(job, "Failed to parse article: "+err.Error())
		return
	}
	job.Content = content

	ac.updateJobStatus(job, StatusGenerating)

	// Generate audio
	audioData, err := ac.audioGen.GenerateAudio(content)
	if err != nil {
		ac.handleJobError(job, "Failed to generate audio: "+err.Error())
		return
	}

	// Calculate duration
	durationSeconds, err := audio.CalculateMP3Duration(audioData)
	if err != nil {
		log.Printf("Warning: Failed to calculate MP3 duration: %v", err)
		durationSeconds = 0 // Default to 0 if calculation fails
	}
	job.Duration = float64(durationSeconds)

	ac.updateJobStatus(job, StatusUploading)

	// Upload to storage with userID
	filename := job.ID + ".mp3"
	err = ac.storage.UploadAudio(userID, filename, audioData)
	if err != nil {
		ac.handleJobError(job, "Failed to upload audio: "+err.Error())
		return
	}

	job.AudioFileName = filename

	// After successful upload, update RSS feed
	feed, err := ac.rssService.GetOrCreateFeed(userID, "User", "user@example.com")
	if err != nil {
		log.Printf("Warning: Failed to get/create RSS feed: %v", err)
	} else {
		audioURL := fmt.Sprintf("https://%s.s3.amazonaws.com/%s/%s",
			ac.storage.GetBucketName(),
			userID,
			job.AudioFileName)

		// Use filename as title and provide default values for missing fields
		title := job.AudioFileName
		author := "Article2Audio User"
		description := fmt.Sprintf("Audio version of article from: %s", job.URL)

		ac.rssService.AddItem(feed, title, author, description, audioURL, job.Duration)

		err = ac.rssService.SaveFeed(userID, feed)
		if err != nil {
			log.Printf("Warning: Failed to save RSS feed: %v", err)
		}
	}

	ac.updateJobStatus(job, StatusCompleted)
}

func (ac *AudioConverter) updateJobStatus(job *ConversionJob, status ConversionStatus) {
	ac.mu.Lock()
	defer ac.mu.Unlock()
	job.Status = status
}

func (ac *AudioConverter) handleJobError(job *ConversionJob, errorMsg string) {
	ac.mu.Lock()
	defer ac.mu.Unlock()
	job.Status = StatusFailed
	job.Error = errorMsg
}
