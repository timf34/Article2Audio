package storage

import (
	"bytes"
	"fmt"
	"github.com/aws/aws-sdk-go/aws"
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

func (s *S3Storage) ListAudioFiles(userID string) ([]string, error) {

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

	var files []string
	for _, obj := range result.Contents {
		files = append(files, *obj.Key)
	}
	return files, nil
}
