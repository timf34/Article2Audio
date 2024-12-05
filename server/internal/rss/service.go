package rss

import (
	"encoding/xml"
	"fmt"
	"log"
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

type Channel struct {
	XMLName     xml.Name `xml:"channel"`
	Title       string   `xml:"title"`
	Link        string   `xml:"link"`
	Language    string   `xml:"language"`
	Copyright   string   `xml:"copyright"`
	Description string   `xml:"description"`
	Items       []Item   `xml:"item"`

	// iTunes specific fields - note the namespace prefix
	ITunesAuthor   string   `xml:"itunes:author,omitempty"`
	ITunesImage    Image    `xml:"itunes:image,omitempty"`
	ITunesCategory Category `xml:"itunes:category,omitempty"`
	ITunesExplicit string   `xml:"itunes:explicit,omitempty"`
	ITunesOwner    Owner    `xml:"itunes:owner,omitempty"`

	// Atom Link
	AtomLink AtomLink `xml:"atom:link"`
}

type AtomLink struct {
	Href string `xml:"href,attr"`
}

type Image struct {
	Href string `xml:"href,attr"`
}

type Category struct {
	Text string `xml:"text,attr"`
}

type Owner struct {
	Name  string `xml:"itunes:name"`
	Email string `xml:"itunes:email"`
}

type Item struct {
	Title          string    `xml:"title"`
	Description    string    `xml:"description"`
	PubDate        string    `xml:"pubDate"`
	Enclosure      Enclosure `xml:"enclosure"`
	GUID           GUID      `xml:"guid"`
	ITunesDuration string    `xml:"itunes:duration,omitempty"`
	ITunesExplicit string    `xml:"itunes:explicit,omitempty"`
	ITunesAuthor   string    `xml:"itunes:author,omitempty"`
}

type RSS struct {
	XMLName xml.Name `xml:"rss"`
	Version string   `xml:"version,attr"`
	// Add namespace definitions
	ITunes  string  `xml:"xmlns:itunes,attr"`
	Content string  `xml:"xmlns:content,attr"`
	Atom    string  `xml:"xmlns:atom,attr"`
	Channel Channel `xml:"channel"`
}

type Enclosure struct {
	URL    string `xml:"url,attr"`
	Length string `xml:"length,attr"`
	Type   string `xml:"type,attr"`
}

type GUID struct {
	Value       string `xml:",chardata"`
	IsPermaLink string `xml:"isPermaLink,attr"`
}

func New(storage StorageInterface) *RSSService {
	return &RSSService{
		storage: storage,
	}
}

func (s *RSSService) CreateInitialFeed(userID, name, email string) (*RSS, error) {
	feed := &RSS{
		Version: "2.0",
		ITunes:  "http://www.itunes.com/dtds/podcast-1.0.dtd",
		Content: "http://purl.org/rss/1.0/modules/content/",
		Atom:    "http://www.w3.org/2005/Atom",
		Channel: Channel{
			Title:          fmt.Sprintf("%s's Articles", name),
			Link:           "https://article2audio.com",
			Language:       "en-us",
			Copyright:      fmt.Sprintf("© %d %s", time.Now().Year(), name),
			ITunesAuthor:   name,
			Description:    fmt.Sprintf("%s's articles", name),
			ITunesExplicit: "false",
			ITunesOwner: Owner{
				Name:  name,
				Email: email,
			},
			ITunesImage: Image{
				Href: "https://article2audio.com/podcast_cover.jpg",
			},
			ITunesCategory: Category{
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

	// Create unique GUID using timestamp and random string
	guid := fmt.Sprintf("%s-%d", time.Now().Format("20060102150405"), time.Now().UnixNano()%10000)

	newItem := Item{
		Title:          title,
		ITunesAuthor:   author,
		Description:    description,
		PubDate:        time.Now().Format(time.RFC1123Z),
		ITunesDuration: duration,
		ITunesExplicit: "false",
		GUID: GUID{
			Value:       guid,
			IsPermaLink: "false",
		},
		Enclosure: Enclosure{
			URL:    audioURL,
			Type:   "audio/mpeg",
			Length: "0", // You might want to add actual file size here
		},
	}

	feed.Channel.Items = append([]Item{newItem}, feed.Channel.Items...)
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
		fmt.Printf("Here is the raw data: %s\n", string(data))

		var feed RSS
		if err := xml.Unmarshal(data, &feed); err != nil {
			return nil, fmt.Errorf("error unmarshaling feed: %v", err)
		}

		// Ensure namespaces are set
		feed.ITunes = "http://www.itunes.com/dtds/podcast-1.0.dtd"
		feed.Content = "http://purl.org/rss/1.0/modules/content/"
		feed.Atom = "http://www.w3.org/2005/Atom"

		// Update feed metadata
		feed.Channel.Title = fmt.Sprintf("%s's Articles", name)
		feed.Channel.Copyright = fmt.Sprintf("© %d %s", time.Now().Year(), name)
		feed.Channel.ITunesAuthor = name
		feed.Channel.ITunesOwner.Name = name
		feed.Channel.ITunesOwner.Email = email

		return &feed, nil
	}

	return s.CreateInitialFeed(userID, name, email)
}

func (s *RSSService) SaveFeed(userID string, feed *RSS) error {
	// Validate items before saving
	for i, item := range feed.Channel.Items {
		log.Printf("Validating item %d: %s", i, item.Title)
		if item.ITunesDuration == "" {
			log.Printf("Warning: Item %s has no duration", item.Title)
		}
		if item.ITunesAuthor == "" {
			log.Printf("Warning: Item %s has no author", item.Title)
		}
	}

	// Print feed items before marshaling
	log.Printf("\nFeed items before saving:")
	for i, item := range feed.Channel.Items {
		log.Printf("Item %d before marshal:\n  Title: %s\n  Duration: %s\n  Author: %s\n",
			i, item.Title, item.ITunesDuration, item.ITunesAuthor)
	}

	output, err := xml.MarshalIndent(feed, "", "  ")
	if err != nil {
		return fmt.Errorf("error marshaling RSS feed: %v", err)
	}

	// Print the final XML
	log.Printf("\nFinal XML to be saved:\n%s", string(output))

	xmlData := append([]byte(xml.Header), output...)
	return s.storage.UploadFile(userID, "rss.xml", xmlData)
}
