package rss

import (
	"encoding/xml"
	"fmt"
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

	// iTunes specific fields
	ITunesAuthor   string   `xml:"itunes:author"`
	ITunesImage    Image    `xml:"itunes:image"`
	ITunesCategory Category `xml:"itunes:category"`
	ITunesExplicit string   `xml:"itunes:explicit"`
	ITunesOwner    Owner    `xml:"itunes:owner"`
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
	ITunesDuration string    `xml:"itunes:duration"`
	ITunesExplicit string    `xml:"itunes:explicit"`
	ITunesAuthor   string    `xml:"itunes:author"`
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

type RSS struct {
	XMLName xml.Name `xml:"rss"`
	Version string   `xml:"version,attr"`
	ITunes  string   `xml:"xmlns:itunes,attr"`
	Content string   `xml:"xmlns:content,attr"`
	Atom    string   `xml:"xmlns:atom,attr"`
	Channel Channel  `xml:"channel"`
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

	item := Item{
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

	feed.Channel.Items = append([]Item{item}, feed.Channel.Items...) // Add new items at the start
}

func (s *RSSService) SaveFeed(userID string, feed *RSS) error {
	// Convert feed to XML
	output, err := xml.MarshalIndent(feed, "", "  ")
	if err != nil {
		return fmt.Errorf("error marshaling RSS feed: %v", err)
	}

	// Add XML header
	xmlData := append([]byte(xml.Header), output...)

	// Upload to storage
	err = s.storage.UploadFile(userID, "rss.xml", xmlData)
	if err != nil {
		return fmt.Errorf("error uploading RSS feed: %v", err)
	}

	return nil
}

func (s *RSSService) GetOrCreateFeed(userID, name, email string) (*RSS, error) {
	// Check if feed exists
	exists, err := s.storage.FileExists(userID, "rss.xml")
	if err != nil {
		return nil, fmt.Errorf("error checking feed existence: %v", err)
	}

	if exists {
		// Download existing feed
		data, err := s.storage.DownloadFile(userID, "rss.xml")
		if err != nil {
			return nil, fmt.Errorf("error downloading feed: %v", err)
		}

		var feed RSS
		err = xml.Unmarshal(data, &feed)
		if err != nil {
			return nil, fmt.Errorf("error unmarshaling feed: %v", err)
		}

		// Ensure iTunes namespaces are preserved
		feed.Version = "2.0"
		feed.ITunes = "http://www.itunes.com/dtds/podcast-1.0.dtd"
		feed.Content = "http://purl.org/rss/1.0/modules/content/"
		feed.Atom = "http://www.w3.org/2005/Atom"

		// Ensure channel metadata is preserved
		if feed.Channel.ITunesExplicit == "" {
			feed.Channel.ITunesExplicit = "false"
		}
		if feed.Channel.ITunesAuthor == "" {
			feed.Channel.ITunesAuthor = name
		}
		if feed.Channel.ITunesImage.Href == "" {
			feed.Channel.ITunesImage.Href = "https://article2audio.com/podcast_cover.jpg"
		}
		if feed.Channel.ITunesCategory.Text == "" {
			feed.Channel.ITunesCategory.Text = "Technology"
		}
		if feed.Channel.ITunesOwner.Name == "" {
			feed.Channel.ITunesOwner.Name = name
		}
		if feed.Channel.ITunesOwner.Email == "" {
			feed.Channel.ITunesOwner.Email = email
		}

		// Preserve metadata for existing items
		for i := range feed.Channel.Items {
			if feed.Channel.Items[i].ITunesExplicit == "" {
				feed.Channel.Items[i].ITunesExplicit = "false"
			}
			// Only set author if it's empty
			if feed.Channel.Items[i].ITunesAuthor == "" {
				feed.Channel.Items[i].ITunesAuthor = "Article2Audio User"
			}
		}

		return &feed, nil
	}

	// Create new feed
	return s.CreateInitialFeed(userID, name, email)
}
