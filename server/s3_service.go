package main

import (
	"bytes"
	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/s3"
)

type S3Service struct {
	client *s3.S3
	bucket string
}

func NewS3Service() *S3Service {
	sess := session.Must(session.NewSession(&aws.Config{
		Region: aws.String("your-region"),
	}))

	return &S3Service{
		client: s3.New(sess),
		bucket: "your-bucket-name",
	}
}

func (s *S3Service) UploadAudio(filename string, data []byte) error {
	_, err := s.client.PutObject(&s3.PutObjectInput{
		Bucket: aws.String(s.bucket),
		Key:    aws.String(filename),
		Body:   bytes.NewReader(data),
	})

	return err
}

func (s *S3Service) ListAudioFiles() ([]string, error) {
	result, err := s.client.ListObjectsV2(&s3.ListObjectsV2Input{
		Bucket: aws.String(s.bucket),
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
