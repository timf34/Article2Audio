package main

import (
	"log"

	"article2audio/internal/api"
	"article2audio/internal/article"
	"article2audio/internal/audio"
	"article2audio/internal/auth"
	"article2audio/internal/conversion"
	"article2audio/internal/storage"
	"github.com/joho/godotenv"
)

func main() {
	// Load environment variables
	if err := godotenv.Load(); err != nil {
		log.Printf("Warning: Error loading .env file: %v", err)
	}

	// Initialize services
	storageService := storage.New()
	openaiService := audio.New()
	articleService := article.New()
	authService := auth.New()
	conversionService := conversion.New(storageService, openaiService, articleService)

	// Initialize and start server
	server := api.NewServer(conversionService, authService)

	log.Printf("Starting server on :8080")
	err := server.Start(":8080")
	if err != nil {
		log.Fatal(err)
	}
}
