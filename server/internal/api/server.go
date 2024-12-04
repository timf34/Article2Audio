package api

import (
	"article2audio/internal/conversion"
	"github.com/gorilla/mux"
	"github.com/rs/cors"
	"net/http"
)

type Server struct {
	router  *mux.Router
	handler *Handler
}

func NewServer(cs *conversion.AudioConverter) *Server {
	s := &Server{
		router: mux.NewRouter(),
	}
	s.handler = NewHandler(cs)
	s.routes()

	// Wrap router with UserAuthMiddleware
	s.router.Use(UserAuthMiddleware)

	return s
}

func (s *Server) routes() {
	s.router.HandleFunc("/convert", s.handler.HandleConversion).Methods("POST")
	s.router.HandleFunc("/status/{jobId}", s.handler.GetConversionStatus).Methods("GET")
	s.router.HandleFunc("/audio-files", s.handler.ListAudioFiles).Methods("GET")
}

func (s *Server) Start(addr string) error {
	// CORS setup
	c := cors.New(cors.Options{
		AllowedOrigins: []string{"http://localhost:3000", "https://article2audio.com"},
		AllowedMethods: []string{"GET", "POST", "OPTIONS"},
		AllowedHeaders: []string{"Content-Type", "Authorization"},
	})

	return http.ListenAndServe(addr, c.Handler(s.router))
}
