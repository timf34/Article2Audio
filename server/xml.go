package main

import (
	"encoding/xml"
	"fmt"
	"io/ioutil"
	"os"
)

type RSS struct {
	Channel Channel `xml:"channel"`
}

type Channel struct {
	Items []Item `xml:"item"`
}

type Item struct {
	Title       string    `xml:"title"`
	Author      string    `xml:"itunes:author"`
	Description string    `xml:"description"`
	PubDate     string    `xml:"pubDate"`
	Enclosure   Enclosure `xml:"enclosure"`
	GUID        string    `xml:"guid"`
	Duration    string    `xml:"itunes:duration"`
	Explicit    string    `xml:"itunes:explicit"`
}

type Enclosure struct {
	URL    string `xml:"url,attr"`
	Length string `xml:"length,attr"`
	Type   string `xml:"type,attr"`
}

func main() {
	// Open the XML file
	xmlFile, err := os.Open("test.xml")
	if err != nil {
		fmt.Println("Error opening file:", err)
		return
	}
	defer xmlFile.Close()

	// Read the XML file contents
	byteValue, _ := ioutil.ReadAll(xmlFile)

	// Unmarshal the XML data into the RSS struct
	var rss RSS
	err = xml.Unmarshal(byteValue, &rss)
	if err != nil {
		fmt.Println("Error unmarshaling XML:", err)
		return
	}

	// Print the contents of each <item>
	for i, item := range rss.Channel.Items {
		fmt.Printf("Item %d:\n", i+1)
		fmt.Printf("  Title: %s\n", item.Title)
		fmt.Printf("  Author: %s\n", item.Author)
		fmt.Printf("  Description: %s\n", item.Description)
		fmt.Printf("  PubDate: %s\n", item.PubDate)
		fmt.Printf("  Enclosure:\n")
		fmt.Printf("    URL: %s\n", item.Enclosure.URL)
		fmt.Printf("    Length: %s\n", item.Enclosure.Length)
		fmt.Printf("    Type: %s\n", item.Enclosure.Type)
		fmt.Printf("  GUID: %s\n", item.GUID)
		fmt.Printf("  Duration: %s\n", item.Duration)
		fmt.Printf("  Explicit: %s\n\n", item.Explicit)
	}
}
