package main

import (
    "log"
    "net/http"
    "github.com/gorilla/mux"
    "github.com/rs/cors"
)

func main() {
    r := mux.NewRouter()

    // Initialize services
    s3Service := NewS3Service()
    openaiService := NewOpenAIService()
    conversionService := NewConversionService(s3Service, openaiService)

    // Initialize handlers
    handler := NewHandler(conversionService)

    // Routes
    r.HandleFunc("/convert", handler.HandleConversion).Methods("POST")
    r.HandleFunc("/status/{jobId}", handler.GetConversionStatus).Methods("GET")
    r.HandleFunc("/audio-files", handler.ListAudioFiles).Methods("GET")

    // CORS
    c := cors.New(cors.Options{
        AllowedOrigins: []string{"http://localhost:3000", "https://your-frontend-domain.com"},
        AllowedMethods: []string{"GET", "POST", "OPTIONS"},
        AllowedHeaders: []string{"Content-Type", "Authorization"},
    })

    log.Fatal(http.ListenAndServe(":8080", c.Handler(r)))
}