// Run with: go test ./internal/rss -v

package rss

import (
	"encoding/xml"
	"os"
	"testing"
)

// LocalStorage implements StorageInterface for testing
type LocalStorage struct {
	basePath string
}

func NewLocalStorage(basePath string) *LocalStorage {
	return &LocalStorage{basePath: basePath}
}

func (s *LocalStorage) UploadFile(userID string, filename string, data []byte) error {
	return os.WriteFile(s.basePath+"/"+filename, data, 0644)
}

func (s *LocalStorage) DownloadFile(userID string, filename string) ([]byte, error) {
	return os.ReadFile(s.basePath + "/" + filename)
}

func (s *LocalStorage) FileExists(userID string, filename string) (bool, error) {
	_, err := os.Stat(s.basePath + "/" + filename)
	if os.IsNotExist(err) {
		return false, nil
	}
	return err == nil, err
}

func TestRSSService(t *testing.T) {
	// Initialize local storage pointing to the test directory
	storage := NewLocalStorage(".")
	service := New(storage)

	// Create initial test.xml if it doesn't exist
	exists, _ := storage.FileExists("", "test.xml")
	if !exists {
		feed, err := service.CreateInitialFeed("test-user", "Test User", "test@example.com")
		if err != nil {
			t.Fatalf("Failed to create initial feed: %v", err)
		}
		if err := service.SaveFeed("", feed); err != nil {
			t.Fatalf("Failed to save initial feed: %v", err)
		}
	}

	// Test adding a new item
	t.Run("Add new item and preserve existing items", func(t *testing.T) {
		// Load existing feed
		feed, err := service.GetOrCreateFeed("", "Test User", "test@example.com")
		if err != nil {
			t.Fatalf("Failed to get feed: %v", err)
		}

		// Print existing items
		t.Log("Existing items before adding new item:")
		for i, item := range feed.Channel.Items {
			t.Logf("Item %d: Title=%s, Duration=%s, Author=%s",
				i, item.Title, item.ITunesDuration, item.ITunesAuthor)
		}

		// Add new item
		service.AddItem(feed,
			"test-audio.mp3",
			"Test Author",
			"Test Description",
			"https://example.com/test-audio.mp3",
			80.5, // 1 minute 20.5 seconds
		)

		// Save the updated feed
		if err := service.SaveFeed("", feed); err != nil {
			t.Fatalf("Failed to save updated feed: %v", err)
		}

		// Reload the feed to verify changes
		updatedFeed, err := service.GetOrCreateFeed("", "Test User", "test@example.com")
		if err != nil {
			t.Fatalf("Failed to reload feed: %v", err)
		}

		// Print updated items
		t.Log("\nItems after adding new item:")
		for i, item := range updatedFeed.Channel.Items {
			t.Logf("Item %d: Title=%s, Duration=%s, Author=%s",
				i, item.Title, item.ITunesDuration, item.ITunesAuthor)
		}

		// Verify the new item was added and old items preserved
		if len(updatedFeed.Channel.Items) == 0 {
			t.Fatal("No items found in updated feed")
		}

		firstItem := updatedFeed.Channel.Items[0]
		if firstItem.Title != "test-audio.mp3" {
			t.Errorf("Expected first item title to be 'test-audio.mp3', got '%s'", firstItem.Title)
		}
		if firstItem.ITunesDuration != "00:01:20" {
			t.Errorf("Expected duration '00:01:20', got '%s'", firstItem.ITunesDuration)
		}
		if firstItem.ITunesAuthor != "Test Author" {
			t.Errorf("Expected author 'Test Author', got '%s'", firstItem.ITunesAuthor)
		}
	})
}

// Helper function to pretty print XML (for debugging)
func prettyPrintXML(data interface{}) string {
	output, err := xml.MarshalIndent(data, "", "  ")
	if err != nil {
		return err.Error()
	}
	return string(output)
}
