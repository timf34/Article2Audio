// internal/audio/duration_test.go
package audio

import (
	"os"
	"testing"
)

func TestCalculateMP3Duration(t *testing.T) {
	// Test file path - update this to match your local MP3 file
	testFile := "./test.mp3"

	// Read the test file
	data, err := os.ReadFile(testFile)
	if err != nil {
		t.Fatalf("Failed to read test file: %v", err)
	}

	// Print file size
	t.Logf("File size: %d bytes", len(data))

	// Calculate duration
	duration, err := CalculateMP3Duration(data)
	if err != nil {
		t.Fatalf("Failed to calculate duration: %v", err)
	}

	// Print the duration
	t.Logf("MP3 Duration: %d seconds", duration)
}
