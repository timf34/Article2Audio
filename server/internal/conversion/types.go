package conversion

type ConversionStatus string

type ConversionJob struct {
	ID            string
	URL           string
	Status        ConversionStatus
	Content       string
	AudioFileName string
	Error         string
	UserID        string
}

const (
	StatusPending    ConversionStatus = "PENDING"
	StatusParsing    ConversionStatus = "PARSING"
	StatusGenerating ConversionStatus = "GENERATING_AUDIO"
	StatusUploading  ConversionStatus = "UPLOADING"
	StatusCompleted  ConversionStatus = "COMPLETED"
	StatusFailed     ConversionStatus = "FAILED"
)

type ConversionRequest struct {
	URL string `json:"url"`
}

type ConversionResponse struct {
	JobID         string           `json:"jobId"`
	Status        ConversionStatus `json:"status"`
	EstimatedTime int              `json:"estimatedTime"`
	Error         string           `json:"error,omitempty"`
}
