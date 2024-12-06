package storage

import (
	"bytes"
	"fmt"
	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/awserr"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/s3"
	"log"
)

type S3Storage struct {
	client *s3.S3
	bucket string
}

func New() *S3Storage {
	sess := session.Must(session.NewSession(&aws.Config{
		Region: aws.String("eu-west-1"),
	}))

	return &S3Storage{
		client: s3.New(sess),
		bucket: "article2audio",
	}
}

func (s *S3Storage) UploadAudio(userID string, filename string, data []byte) error {
	if userID == "" {
		return fmt.Errorf("userID cannot be empty")
	}
	key := fmt.Sprintf("%s/%s", userID, filename)

	log.Printf("Starting upload to S3: Bucket=%s, Key=%s", s.bucket, key)

	metadata := map[string]*string{} // Metadata can be added here as needed

	_, err := s.client.PutObject(&s3.PutObjectInput{
		Bucket:   aws.String(s.bucket),
		Key:      aws.String(key),
		Body:     bytes.NewReader(data),
		Metadata: metadata,
	})

	if err != nil {
		log.Printf("Failed to upload file to S3: Bucket=%s, Filename=%s, Error=%v", s.bucket, filename, err)
		return err
	}

	log.Printf("Successfully uploaded file to S3: Bucket=%s, Key=%s", s.bucket, key)
	return nil
}

type AudioFile struct {
	Key       string
	CreatedAt string
}

func (s *S3Storage) ListAudioFiles(userID string) ([]AudioFile, error) {
	if userID == "" {
		return nil, fmt.Errorf("userID cannot be empty")
	}

	prefix := fmt.Sprintf("%s/", userID)
	result, err := s.client.ListObjectsV2(&s3.ListObjectsV2Input{
		Bucket: aws.String(s.bucket),
		Prefix: aws.String(prefix),
	})

	if err != nil {
		return nil, fmt.Errorf("failed to list files for user %s: %v", userID, err)
	}

	if len(result.Contents) == 0 {
            return []AudioFile{}, nil  // Return empty list if no files found
    }

	var files []AudioFile
	for _, obj := range result.Contents {
		files = append(files, AudioFile{
			Key:       *obj.Key,
			CreatedAt: obj.LastModified.Format("2006-01-02T15:04:05Z"), // ISO 8601 format
		})
	}
	return files, nil
}

func (s *S3Storage) UploadFile(userID string, filename string, data []byte) error {
	return s.UploadAudio(userID, filename, data) // Reuse existing upload function
}

func (s *S3Storage) DownloadFile(userID string, filename string) ([]byte, error) {
	key := fmt.Sprintf("%s/%s", userID, filename)

	result, err := s.client.GetObject(&s3.GetObjectInput{
		Bucket: aws.String(s.bucket),
		Key:    aws.String(key),
	})
	if err != nil {
		return nil, fmt.Errorf("failed to download file: %v", err)
	}
	defer result.Body.Close()

	buf := new(bytes.Buffer)
	_, err = buf.ReadFrom(result.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read file: %v", err)
	}

	return buf.Bytes(), nil
}

func (s *S3Storage) FileExists(userID string, filename string) (bool, error) {
	key := fmt.Sprintf("%s/%s", userID, filename)

	_, err := s.client.HeadObject(&s3.HeadObjectInput{
		Bucket: aws.String(s.bucket),
		Key:    aws.String(key),
	})

	if err != nil {
		// Check if error is because file doesn't exist
		if aerr, ok := err.(awserr.Error); ok {
			if aerr.Code() == "NotFound" {
				return false, nil
			}
		}
		return false, err
	}

	return true, nil
}

func (s *S3Storage) GetBucketName() string {
	return s.bucket
}
