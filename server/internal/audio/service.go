package audio

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"strings"
	"sync"
)

// ChunkResult holds the result of processing a single chunk
type ChunkResult struct {
	Index int
	Data  []byte
	Error error
}

type Audio struct {
	apiKey string
}

func New() *Audio {
	apiKey := os.Getenv("OPENAI_KEY")
	if apiKey == "" {
		log.Println("Warning: OPENAI_KEY environment variable is not set")
	}
	return &Audio{
		apiKey: apiKey,
	}
}

// splitTextIntoChunks splits text into chunks of maximum size while preserving sentences
func splitTextIntoChunks(text string, maxChunkSize int) []string {
	// Split text into sentences
	sentences := strings.Split(strings.ReplaceAll(text, ". ", ".|"), "|")

	var chunks []string
	currentChunk := ""

	for _, sentence := range sentences {
		// Clean up the sentence
		sentence = strings.TrimSpace(sentence)
		if sentence == "" {
			continue
		}

		// Add period back if it was removed during split
		if !strings.HasSuffix(sentence, ".") {
			sentence += "."
		}

		// If adding this sentence would exceed chunk size, start a new chunk
		if len(currentChunk)+len(sentence)+1 > maxChunkSize {
			if currentChunk != "" {
				chunks = append(chunks, strings.TrimSpace(currentChunk))
			}
			currentChunk = sentence + " "
		} else {
			currentChunk += sentence + " "
		}
	}

	// Add the last chunk if it's not empty
	if currentChunk != "" {
		chunks = append(chunks, strings.TrimSpace(currentChunk))
	}

	return chunks
}

func (s *Audio) generateChunk(text string, index int, resultChan chan<- ChunkResult) {
	url := "https://api.openai.com/v1/audio/speech"

	requestBody := map[string]string{
		"model": "tts-1",
		"input": text,
		"voice": "alloy",
	}

	jsonData, err := json.Marshal(requestBody)
	if err != nil {
		resultChan <- ChunkResult{Index: index, Error: fmt.Errorf("error marshaling request: %v", err)}
		return
	}

	req, err := http.NewRequest("POST", url, bytes.NewBuffer(jsonData))
	if err != nil {
		resultChan <- ChunkResult{Index: index, Error: fmt.Errorf("error creating request: %v", err)}
		return
	}

	req.Header.Set("Authorization", "Bearer "+s.apiKey)
	req.Header.Set("Content-Type", "application/json")

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		resultChan <- ChunkResult{Index: index, Error: fmt.Errorf("error making request: %v", err)}
		return
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		bodyBytes, _ := io.ReadAll(resp.Body)
		resultChan <- ChunkResult{Index: index, Error: fmt.Errorf("OpenAI API error (status %d): %s", resp.StatusCode, string(bodyBytes))}
		return
	}

	audioData, err := io.ReadAll(resp.Body)
	if err != nil {
		resultChan <- ChunkResult{Index: index, Error: fmt.Errorf("error reading response: %v", err)}
		return
	}

	resultChan <- ChunkResult{Index: index, Data: audioData}
}

// GenerateAudio processes the text in chunks concurrently
func (s *Audio) GenerateAudio(text string) ([]byte, error) {
	log.Printf("Starting audio generation for text of length %d characters", len(text))

	const maxChunkSize = 2048 // Maximum characters per chunk
	chunks := splitTextIntoChunks(text, maxChunkSize)

	if len(chunks) == 0 {
		return nil, fmt.Errorf("no text to process")
	}

	// If text fits in a single chunk, process it directly
	if len(chunks) == 1 {
		resultChan := make(chan ChunkResult, 1)
		s.generateChunk(chunks[0], 0, resultChan)
		result := <-resultChan
		return result.Data, result.Error
	}

	// Process chunks concurrently
	resultChan := make(chan ChunkResult, len(chunks))
	var wg sync.WaitGroup

	// Limit concurrent requests to avoid overwhelming the server
	semaphore := make(chan struct{}, 3) // Max 3 concurrent requests

	for i, chunk := range chunks {
		wg.Add(1)
		go func(idx int, text string) {
			defer wg.Done()
			semaphore <- struct{}{}        // Acquire semaphore
			defer func() { <-semaphore }() // Release semaphore
			s.generateChunk(text, idx, resultChan)
		}(i, chunk)
	}

	// Close result channel when all goroutines complete
	go func() {
		wg.Wait()
		close(resultChan)
	}()

	// Collect results in order
	results := make([][]byte, len(chunks))
	for result := range resultChan {
		if result.Error != nil {
			return nil, fmt.Errorf("error processing chunk %d: %v", result.Index, result.Error)
		}
		results[result.Index] = result.Data
	}

	// Combine audio chunks
	totalSize := 0
	for _, data := range results {
		totalSize += len(data)
	}

	combinedAudio := make([]byte, 0, totalSize)
	for _, data := range results {
		combinedAudio = append(combinedAudio, data...)
	}

	log.Printf("Successfully generated audio from %d chunks, total size: %d bytes", len(chunks), len(combinedAudio))
	return combinedAudio, nil
}
