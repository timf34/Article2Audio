package rss

import (
	"github.com/mmcdole/gofeed"
	"os"
	"testing"
)

// LocalStorage implements StorageInterface for testing
type LocalStorage struct {
	basePath string
}

func (s *LocalStorage) DownloadFile(_ string, filename string) ([]byte, error) {
	return os.ReadFile(filename)
}

func (s *LocalStorage) UploadFile(_ string, filename string, data []byte) error {
	return os.WriteFile(filename, data, 0644)
}

func (s *LocalStorage) FileExists(_ string, filename string) (bool, error) {
	_, err := os.Stat(filename)
	if err == nil {
		return true, nil
	}
	if os.IsNotExist(err) {
		return false, nil
	}
	return false, err
}

func TestRSSService(t *testing.T) {
	// Create service with local storage
	storage := &LocalStorage{basePath: "."}
	service := New(storage)

	t.Run("Read and Modify Feed", func(t *testing.T) {
		// Load and parse test.xml
		data, err := storage.DownloadFile("", "test.xml")
		if err != nil {
			t.Fatalf("Failed to read test.xml: %v", err)
		}

		t.Logf("Original RSS Feed:\n%s", string(data))

		// Parse using gofeed
		parser := gofeed.NewParser()
		gofeedFeed, err := parser.ParseString(string(data))
		if err != nil {
			t.Fatalf("Failed to parse feed: %v", err)
		}

		// Convert to our RSS struct
		feed := &RSS{
			Version: "2.0",
			Itunes:  "http://www.itunes.com/dtds/podcast-1.0.dtd",
			Content: "http://purl.org/rss/1.0/modules/content/",
			Atom:    "http://www.w3.org/2005/Atom",
			Channel: Channel{
				Title:          gofeedFeed.Title,
				Link:           gofeedFeed.Link,
				Language:       gofeedFeed.Language,
				Copyright:      gofeedFeed.Copyright,
				ItunesAuthor:   gofeedFeed.ITunesExt.Author,
				Description:    gofeedFeed.Description,
				ItunesImage:    Image{Href: gofeedFeed.Image.URL},
				ItunesCategory: Category{Text: gofeedFeed.Categories[0]},
				ItunesExplicit: gofeedFeed.ITunesExt.Explicit,
				AtomLink: AtomLink{
					Href: "https://article2audio.com/rss.xml",
					Rel:  "self",
					Type: "application/rss+xml",
				},
				Items: convertItems(gofeedFeed.Items),
			},
		}

		// Print existing items
		t.Log("\nExisting items in feed:")
		for i, item := range feed.Channel.Items {
			t.Logf("Item %d:\n  Title: %s\n  Duration: %s\n  Author: %s",
				i, item.Title, item.ItunesDuration, item.ItunesAuthor)
		}
		originalItemCount := len(feed.Channel.Items)

		// Test adding a new item
		service.AddItem(feed,
			"Test Article",
			"Test Author",
			"This is a test article description",
			"https://example.com/test-audio.mp3",
			300.0) // 5 minutes duration

		// Verify new item was added
		if len(feed.Channel.Items) != originalItemCount+1 {
			t.Errorf("Expected %d items, got %d", originalItemCount+1, len(feed.Channel.Items))
		}

		// Verify new item is first in the list
		newItem := feed.Channel.Items[0]
		if newItem.Title != "Test Article" {
			t.Errorf("Expected new item title 'Test Article', got '%s'", newItem.Title)
		}
		if newItem.ItunesAuthor != "Test Author" {
			t.Errorf("Expected new item author 'Test Author', got '%s'", newItem.ItunesAuthor)
		}
		if newItem.ItunesDuration != "00:05:00" {
			t.Errorf("Expected duration '00:05:00', got '%s'", newItem.ItunesDuration)
		}

		// Test saving the modified feed
		if err := service.SaveFeed("", feed); err != nil {
			t.Fatalf("Failed to save feed: %v", err)
		}

		// Verify saved file exists and can be parsed
		savedData, err := storage.DownloadFile("", "rss.xml")
		if err != nil {
			t.Fatalf("Failed to read saved file: %v", err)
		}

		// Parse saved file with gofeed to verify it's valid
		savedGofeedFeed, err := parser.ParseString(string(savedData))
		if err != nil {
			t.Fatalf("Failed to parse saved feed: %v", err)
		}

		// Verify saved feed has correct number of items
		if len(savedGofeedFeed.Items) != len(feed.Channel.Items) {
			t.Errorf("Saved feed has %d items, expected %d", len(savedGofeedFeed.Items), len(feed.Channel.Items))
		}

		// Print the items from saved feed
		t.Log("\nSaved feed items:")
		for i, item := range savedGofeedFeed.Items {
			t.Logf("Item %d:\n  Title: %s\n  Duration: %s\n  Author: %s",
				i, item.Title, item.ITunesExt.Duration, item.ITunesExt.Author)
		}
	})
}
