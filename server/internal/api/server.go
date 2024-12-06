package api

import (
	"article2audio/internal/auth"
	"article2audio/internal/conversion"
	"github.com/gorilla/mux"
	"github.com/rs/cors"
	"net/http"
)

type Server struct {
	router      *mux.Router
	handler     *Handler
	authService *auth.Auth0Service
}

func NewServer(cs *conversion.AudioConverter, as *auth.Auth0Service) *Server {
	s := &Server{
		router:      mux.NewRouter(),
		authService: as,
	}
	s.handler = NewHandler(cs)
	s.routes()

	// Wrap router with UserAuthMiddleware, passing the auth service
	s.router.Use(UserAuthMiddleware(s.authService))

	return s
}

func (s *Server) routes() {
	s.router.HandleFunc("/convert", s.handler.HandleConversion).Methods("POST")
	s.router.HandleFunc("/status/{jobId}", s.handler.GetConversionStatus).Methods("GET")
	s.router.HandleFunc("/audio-files", s.handler.ListAudioFiles).Methods("GET")
}

func (s *Server) Start(addr string) error {
	// Update CORS configuration to allow Authorization header
	c := cors.New(cors.Options{
		AllowedOrigins: []string{"http://localhost:3000", "https://article2audio.com"},
		AllowedMethods: []string{"GET", "POST", "OPTIONS"},
		AllowedHeaders: []string{"Content-Type", "Authorization"},
		// Important: Allow credentials for auth headers
		AllowCredentials: true,
	})

	return http.ListenAndServe(addr, c.Handler(s.router))
}
