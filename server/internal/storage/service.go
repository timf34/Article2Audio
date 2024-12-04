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
	log.Printf("Starting upload to S3: Bucket=%s, Filename=%s", s.bucket, filename)

	key := filename
	if userID != "" { // Prefix with userID if provided
		key = fmt.Sprintf("%s/%s", userID, filename)
	}

	metadata := map[string]*string{} // empty for now

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

	log.Printf("Successfully uploaded file to S3: Bucket=%s, Filename=%s", s.bucket, filename)
	return nil
}

func (s *S3Storage) ListAudioFiles(userID string) ([]string, error) {
	prefix := ""
	if userID != "" { // Filter files by userID prefix if provided
		prefix = fmt.Sprintf("%s/", userID)
	}
	result, err := s.client.ListObjectsV2(&s3.ListObjectsV2Input{
		Bucket: aws.String(s.bucket),
		Prefix: aws.String(prefix),
	})
	if err != nil {
		return nil, err
	}

	var files []string
	for _, obj := range result.Contents {
		files = append(files, *obj.Key)
	}
	return files, nil
}
