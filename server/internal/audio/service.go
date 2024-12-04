package audio

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
)

type Audio struct {
	apiKey string
}

func New() *Audio {
	return &Audio{
		apiKey: os.Getenv("OPENAI_API_KEY"),
	}
}

func (s *Audio) GenerateAudio(text string) ([]byte, error) {
	url := "https://api.openai.com/v1/audio/speech"

	requestBody := map[string]string{
		"model": "tts-1",
		"input": text,
		"voice": "alloy",
	}

	jsonData, err := json.Marshal(requestBody)
	if err != nil {
		return nil, err
	}

	req, err := http.NewRequest("POST", url, bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, err
	}

	req.Header.Set("Authorization", "Bearer "+s.apiKey)
	req.Header.Set("Content-Type", "application/json")

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("OpenAI API error: %s", resp.Status)
	}

	return io.ReadAll(resp.Body)
}
