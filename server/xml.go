package main

import (
	"fmt"
	"github.com/mmcdole/gofeed"
	"os"
)

func main() {
	// Open the RSS file
	file, err := os.Open("test.xml")
	if err != nil {
		panic(fmt.Sprintf("Failed to open file: %v", err))
	}
	defer file.Close()

	// Parse the RSS feed
	parser := gofeed.NewParser()
	feed, err := parser.Parse(file)
	if err != nil {
		panic(fmt.Sprintf("Failed to parse feed: %v", err))
	}

	// Print the feed's general information
	fmt.Printf("Feed Title: %s\n", feed.Title)
	fmt.Printf("Feed Description: %s\n", feed.Description)

	// Print details for each item
	for i, item := range feed.Items {
		fmt.Printf("\nItem %d:\n", i+1)
		fmt.Printf("  Title: %s\n", item.Title)
		fmt.Printf("  Description: %s\n", item.Description)
		fmt.Printf("  Published: %s\n", item.Published)

		// Access iTunes-specific fields
		if item.ITunesExt != nil {
			fmt.Printf("  iTunes Author: %s\n", item.ITunesExt.Author)
			fmt.Printf("  iTunes Duration: %s\n", item.ITunesExt.Duration)
			fmt.Printf("  iTunes Explicit: %s\n", item.ITunesExt.Explicit)
		}
	}
}
