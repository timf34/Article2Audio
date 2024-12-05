package rss

import (
	"encoding/xml"
	"fmt"
	"github.com/mmcdole/gofeed"
	"log"
	"strings"
	"time"
)

type RSSService struct {
	storage StorageInterface
}

type StorageInterface interface {
	UploadFile(userID string, filename string, data []byte) error
	DownloadFile(userID string, filename string) ([]byte, error)
	FileExists(userID string, filename string) (bool, error)
}

// RSSFeed struct for re-encoding
type RSS struct {
	XMLName xml.Name `xml:"rss"`
	Version string   `xml:"version,attr"`
	Itunes  string   `xml:"xmlns:itunes,attr"`
	Content string   `xml:"xmlns:content,attr"`
	Atom    string   `xml:"xmlns:atom,attr"`
	Channel Channel  `xml:"channel"`
}

type Channel struct {
	Title          string      `xml:"title"`
	Link           string      `xml:"link"`
	Language       string      `xml:"language"`
	Copyright      string      `xml:"copyright"`
	ItunesAuthor   string      `xml:"itunes:author"`
	Description    string      `xml:"description"`
	ItunesImage    Image       `xml:"itunes:image"`
	ItunesCategory Category    `xml:"itunes:category"`
	ItunesExplicit string      `xml:"itunes:explicit"`
	AtomLink       AtomLink    `xml:"atom:link"`
	ItunesOwner    ItunesOwner `xml:"itunes:owner"`
	Items          []Item      `xml:"item"`
}

type Image struct {
	Href string `xml:"href,attr"`
}

type Category struct {
	Text string `xml:"text,attr"`
}

type AtomLink struct {
	Href string `xml:"href,attr"`
	Rel  string `xml:"rel,attr"`
	Type string `xml:"type,attr"`
}

type ItunesOwner struct {
	Name  string `xml:"itunes:name"`
	Email string `xml:"itunes:email"`
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

func New(storage StorageInterface) *RSSService {
	return &RSSService{
		storage: storage,
	}
}

func (s *RSSService) CreateInitialFeed(userID, name, email string) (*RSS, error) {
	feed := &RSS{
		Version: "2.0",
		Itunes:  "http://www.itunes.com/dtds/podcast-1.0.dtd",
		Content: "http://purl.org/rss/1.0/modules/content/",
		Atom:    "http://www.w3.org/2005/Atom",
		Channel: Channel{
			Title:          fmt.Sprintf("%s's Articles", name),
			Link:           "https://article2audio.com",
			Language:       "en-us",
			Copyright:      fmt.Sprintf("© %d %s", time.Now().Year(), name),
			ItunesAuthor:   name,
			Description:    fmt.Sprintf("%s's articles", name),
			ItunesExplicit: "false",
			AtomLink: AtomLink{
				Href: "https://article2audio.com/rss.xml",
				Rel:  "self",
				Type: "application/rss+xml",
			},
			ItunesOwner: ItunesOwner{
				Name:  name,
				Email: email,
			},
			ItunesImage: Image{
				Href: "https://article2audio.com/podcast_cover.jpg",
			},
			ItunesCategory: Category{
				Text: "Technology",
			},
		},
	}
	return feed, nil
}

func (s *RSSService) AddItem(feed *RSS, title, author, description, audioURL string, durationSeconds float64) {
	// Format duration as HH:MM:SS
	hours := int(durationSeconds) / 3600
	minutes := (int(durationSeconds) % 3600) / 60
	seconds := int(durationSeconds) % 60
	duration := fmt.Sprintf("%02d:%02d:%02d", hours, minutes, seconds)

	newItem := Item{
		Title:          title,
		ItunesAuthor:   author,
		Description:    description,
		PubDate:        time.Now().Format(time.RFC1123),
		ItunesDuration: duration,
		ItunesExplicit: "false",
		GUID:           fmt.Sprintf("https://article2audio.com/%s", time.Now().Format("20060102150405")),
		Enclosure: Enclosure{
			URL:    audioURL,
			Type:   "audio/mpeg",
			Length: "0", // You might want to add actual file size here
		},
	}

	feed.Channel.Items = append([]Item{newItem}, feed.Channel.Items...)
}

func convertItems(items []*gofeed.Item) []Item {
	var converted []Item
	for _, item := range items {
		var enclosure Enclosure
		if len(item.Enclosures) > 0 {
			enclosure = Enclosure{
				URL:    item.Enclosures[0].URL,
				Length: item.Enclosures[0].Length,
				Type:   item.Enclosures[0].Type,
			}
		}

		converted = append(converted, Item{
			Title:          item.Title,
			Description:    item.Description,
			PubDate:        item.Published,
			Enclosure:      enclosure,
			GUID:           item.GUID,
			ItunesAuthor:   item.ITunesExt.Author,
			ItunesDuration: item.ITunesExt.Duration,
			ItunesExplicit: item.ITunesExt.Explicit,
		})
	}
	return converted
}

func (s *RSSService) GetOrCreateFeed(userID, name, email string) (*RSS, error) {
	exists, err := s.storage.FileExists(userID, "rss.xml")
	if err != nil {
		return nil, fmt.Errorf("error checking feed existence: %v", err)
	}

	if exists {
		data, err := s.storage.DownloadFile(userID, "rss.xml")
		if err != nil {
			return nil, fmt.Errorf("error downloading feed: %v", err)
		}

		// Parse the RSS feed using gofeed
		parser := gofeed.NewParser()
		feed, err := parser.ParseString(string(data))
		if err != nil {
			return nil, fmt.Errorf("error parsing feed: %v", err)
		}

		// Convert the parsed feed into our RSS struct
		rssFeed := &RSS{
			Version: "2.0",
			Itunes:  "http://www.itunes.com/dtds/podcast-1.0.dtd",
			Content: "http://purl.org/rss/1.0/modules/content/",
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
				AtomLink: AtomLink{
					Href: "https://article2audio.com/rss.xml",
					Rel:  "self",
					Type: "application/rss+xml",
				},
				ItunesOwner: ItunesOwner{
					Name:  name,
					Email: email,
				},
				Items: convertItems(feed.Items),
			},
		}

		return rssFeed, nil
	}

	return s.CreateInitialFeed(userID, name, email)
}

func (s *RSSService) SaveFeed(userID string, feed *RSS) error {
	// Validate items before saving
	for i, item := range feed.Channel.Items {
		log.Printf("Validating item %d: %s", i, item.Title)
		if item.ItunesDuration == "" {
			log.Printf("Warning: Item %s has no duration", item.Title)
		}
		if item.ItunesAuthor == "" {
			log.Printf("Warning: Item %s has no author", item.Title)
		}
	}

	output, err := xml.MarshalIndent(feed, "", "  ")
	if err != nil {
		return fmt.Errorf("error marshaling RSS feed: %v", err)
	}

	xmlData := append([]byte(xml.Header), output...)
	return s.storage.UploadFile(userID, "rss.xml", xmlData)
}
