package main

import (
	"fmt"
	"github.com/google/uuid"
	"sync"
)

type ConversionService struct {
	jobs          map[string]*ConversionJob
	mu            sync.RWMutex
	s3Service     *S3Service
	openaiService *OpenAIService
}

func NewConversionService(s3 *S3Service, openai *OpenAIService) *ConversionService {
	return &ConversionService{
		jobs:          make(map[string]*ConversionJob),
		s3Service:     s3,
		openaiService: openai,
	}
}

func (cs *ConversionService) StartConversion(url string) (*ConversionJob, error) {
	jobID := uuid.New().String()

	job := &ConversionJob{
		ID:     jobID,
		URL:    url,
		Status: StatusPending,
	}

	cs.mu.Lock()
	cs.jobs[jobID] = job
	cs.mu.Unlock()

	// Start processing in background
	go cs.processJob(job)

	return job, nil
}

func (cs *ConversionService) processJob(job *ConversionJob) {
	// Update status to parsing
	cs.updateJobStatus(job, StatusParsing)

	// Extract article content
	g := goose.New()
	article, err := g.ExtractFromURL(job.URL)
	if err != nil {
		cs.handleJobError(job, "Failed to parse article: "+err.Error())
		return
	}

	job.Content = article.CleanedText

	// Update status to generating audio
	cs.updateJobStatus(job, StatusGenerating)

	// Generate audio using OpenAI
	audioData, err := cs.openaiService.GenerateAudio(job.Content)
	if err != nil {
		cs.handleJobError(job, "Failed to generate audio: "+err.Error())
		return
	}

	// Update status to uploading
	cs.updateJobStatus(job, StatusUploading)

	// Upload to S3
	filename := job.ID + ".mp3"
	err = cs.s3Service.UploadAudio(filename, audioData)
	if err != nil {
		cs.handleJobError(job, "Failed to upload audio: "+err.Error())
		return
	}

	job.AudioFileName = filename
	cs.updateJobStatus(job, StatusCompleted)
}

func (cs *ConversionService) updateJobStatus(job *ConversionJob, status ConversionStatus) {
	cs.mu.Lock()
	defer cs.mu.Unlock()

	job.Status = status
}

func (cs *ConversionService) handleJobError(job *ConversionJob, errorMsg string) {
	cs.mu.Lock()
	defer cs.mu.Unlock()

	job.Status = StatusFailed
	job.Error = errorMsg
}

func (cs *ConversionService) GetStatus(jobID string) (*ConversionJob, error) {
	cs.mu.RLock()
	defer cs.mu.RUnlock()

	job, exists := cs.jobs[jobID]
	if !exists {
		return nil, fmt.Errorf("job not found")
	}

	return job, nil
}

func (cs *ConversionService) ListAudioFiles() ([]string, error) {
	return cs.s3Service.ListAudioFiles()
}
