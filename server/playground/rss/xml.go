package main

import (
	"encoding/xml"
	"fmt"
	"github.com/mmcdole/gofeed"
	"os"
	"strings"
	"time"
)

// RSSFeed struct for re-encoding
type RSSFeed struct {
	XMLName xml.Name `xml:"rss"`
	Version string   `xml:"version,attr"`
	Itunes  string   `xml:"xmlns:itunes,attr"`
	Atom    string   `xml:"xmlns:atom,attr"`
	Channel Channel  `xml:"channel"`
}

type Channel struct {
	Title          string   `xml:"title"`
	Link           string   `xml:"link"`
	Language       string   `xml:"language"`
	Copyright      string   `xml:"copyright"`
	ItunesAuthor   string   `xml:"itunes:author"`
	Description    string   `xml:"description"`
	ItunesImage    Image    `xml:"itunes:image"`
	ItunesCategory Category `xml:"itunes:category"`
	ItunesExplicit string   `xml:"itunes:explicit"`
	Items          []Item   `xml:"item"`
}

type Image struct {
	Href string `xml:"href,attr"`
}

type Category struct {
	Text string `xml:"text,attr"`
}

type Item struct {
	Title          string    `xml:"title"`
	Description    string    `xml:"description"`
	PubDate        string    `xml:"pubDate"`
	Enclosure      Enclosure `xml:"enclosure"`
	GUID           string    `xml:"guid"`
	ItunesAuthor   string    `xml:"itunes:author"`
	ItunesDuration string    `xml:"itunes:duration"`
	ItunesExplicit string    `xml:"itunes:explicit"`
}

type Enclosure struct {
	URL    string `xml:"url,attr"`
	Length string `xml:"length,attr"`
	Type   string `xml:"type,attr"`
}

func main() {
	// Open the RSS file
	file, err := os.Open("test.xml")
	if err != nil {
		panic(fmt.Sprintf("Failed to open file: %v", err))
	}
	defer file.Close()

	// Parse the RSS feed using gofeed
	parser := gofeed.NewParser()
	feed, err := parser.Parse(file)
	if err != nil {
		panic(fmt.Sprintf("Failed to parse feed: %v", err))
	}

	// Convert the parsed feed into a struct we can modify
	rssFeed := RSSFeed{
		Version: "2.0",
		Itunes:  "http://www.itunes.com/dtds/podcast-1.0.dtd",
		Atom:    "http://www.w3.org/2005/Atom",
		Channel: Channel{
			Title:          feed.Title,
			Link:           feed.Link,
			Language:       feed.Language,
			Copyright:      feed.Copyright,
			ItunesAuthor:   feed.ITunesExt.Author,
			Description:    feed.Description,
			ItunesImage:    Image{Href: feed.Image.URL},
			ItunesCategory: Category{Text: strings.Join(feed.Categories, ", ")},
			ItunesExplicit: feed.ITunesExt.Explicit,
			Items:          convertItems(feed.Items),
		},
	}

	// Add a new item
	newItem := Item{
		Title:          "New Article Title",
		Description:    "This is a new article added to the feed.",
		PubDate:        time.Now().Format(time.RFC1123),
		Enclosure:      Enclosure{URL: "https://example.com/new-article.mp3", Length: "1234567", Type: "audio/mpeg"},
		GUID:           "unique-id-for-new-article",
		ItunesAuthor:   "New Author",
		ItunesDuration: "00:10:00",
		ItunesExplicit: "false",
	}

	// Append the new item
	rssFeed.Channel.Items = append(rssFeed.Channel.Items, newItem)

	// Write the updated feed back to the file
	outputFile, err := os.Create("test.xml")
	if err != nil {
		panic(fmt.Sprintf("Failed to create output file: %v", err))
	}
	defer outputFile.Close()

	encoder := xml.NewEncoder(outputFile)
	encoder.Indent("", "  ")
	if err := encoder.Encode(rssFeed); err != nil {
		panic(fmt.Sprintf("Failed to encode RSS feed: %v", err))
	}

	fmt.Println("New item added and RSS feed updated successfully.")
}

func convertItems(items []*gofeed.Item) []Item {
	var converted []Item
	for _, item := range items {
		converted = append(converted, Item{
			Title:          item.Title,
			Description:    item.Description,
			PubDate:        item.Published,
			Enclosure:      Enclosure{URL: item.Enclosures[0].URL, Length: item.Enclosures[0].Length, Type: item.Enclosures[0].Type},
			GUID:           item.GUID,
			ItunesAuthor:   item.ITunesExt.Author,
			ItunesDuration: item.ITunesExt.Duration,
			ItunesExplicit: item.ITunesExt.Explicit,
		})
	}
	return converted
}
