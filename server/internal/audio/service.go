package audio

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
)

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

func (s *Audio) GenerateAudio(text string) ([]byte, error) {
	url := "https://api.openai.com/v1/audio/speech"

	// TODO: Will need to split audio
	// Truncate text if too long (OpenAI has limits)
	text = text[:100]
	if len(text) > 2048 {
		log.Printf("Warning: Text truncated to 4096 characters, but doing just 100 for now\n")
	}

	requestBody := map[string]string{
		"model": "tts-1",
		"input": text,
		"voice": "alloy",
	}

	jsonData, err := json.Marshal(requestBody)
	if err != nil {
		return nil, fmt.Errorf("error marshaling request: %v", err)
	}

	req, err := http.NewRequest("POST", url, bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, fmt.Errorf("error creating request: %v", err)
	}

	req.Header.Set("Authorization", "Bearer "+s.apiKey)
	req.Header.Set("Content-Type", "application/json")

	fmt.Printf("Request: %v", req, "\n")
	log.Printf("Sending request to OpenAI with %d characters of text", len(text))

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("error making request: %v", err)
	}
	defer resp.Body.Close()

	// Read and log error response if status is not OK
	if resp.StatusCode != http.StatusOK {
		bodyBytes, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("OpenAI API error (status %d): %s", resp.StatusCode, string(bodyBytes))
	}

	audioData, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("error reading response: %v", err)
	}

	log.Printf("Successfully generated audio, size: %d bytes", len(audioData))
	return audioData, nil
}
