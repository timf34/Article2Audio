package audio

import (
	"bytes"
	"github.com/tcolgate/mp3"
)

func CalculateMP3Duration(data []byte) (int, error) {
	// Create a reader from the byte data
	reader := bytes.NewReader(data)

	// Create new decoder
	decoder := mp3.NewDecoder(reader)
	var frame mp3.Frame
	var totalDuration float64
	var skipped int

	// Sum up the duration of each frame
	for {
		err := decoder.Decode(&frame, &skipped)
		if err != nil {
			break // End of file or error
		}
		totalDuration += frame.Duration().Seconds()
	}

	// Convert to int seconds
	return int(totalDuration), nil
}
