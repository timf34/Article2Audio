// article_service_test.go
package article

import (
	"fmt"
	"testing"
)

func TestArticleService_ExtractContent(t *testing.T) {
	service := New()

	urls := []string{
		// "https://medium.com/@kentcdodds/write-tests-not-too-many-mostly-integration-5e8c7fff591c",
		// "https://www.theverge.com/23897887/apple-vision-pro-review-vr-ar-headset-features-price",
		"https://www.bbc.com/news/world-us-canada-52241221",
		"https://www.paulgraham.com/getideas.html",
		"https://www.avabear.xyz/p/december-3c2",
	}

	for _, url := range urls {
		content, err := service.ExtractContent(url)
		if err != nil {
			t.Errorf("Failed to extract content from %s: %v", url, err)
			continue
		}
		fmt.Printf("\nExtracted content from %s:\n%s\n", url, content[:300])
		fmt.Println("--------------------------------")
	}
}
