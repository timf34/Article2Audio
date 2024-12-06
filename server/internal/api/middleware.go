package api

import (
	"article2audio/internal/auth"
	"context"
	"log"
	"net/http"
	"os"
	"strings"
)

func UserAuthMiddleware(authService *auth.Auth0Service) func(http.Handler) http.Handler {
	enableAuth := os.Getenv("ENABLE_AUTH") == "true"
	defaultUserID := os.Getenv("DEFAULT_USER_ID")

	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			var userID string

			if enableAuth {
				authHeader := r.Header.Get("Authorization")
				if authHeader == "" {
					http.Error(w, "No authorization header", http.StatusUnauthorized)
					return
				}

				// Remove "Bearer " prefix
				tokenString := strings.TrimPrefix(authHeader, "Bearer ")

				// Validate the token
				sub, err := authService.ValidateToken(tokenString)
				if err != nil {
					log.Printf("Error validating token: %v", err)
					http.Error(w, "Invalid token: "+err.Error(), http.StatusUnauthorized)
					return
				}

				userID = sub
			} else {
				// Use default user ID when authentication is disabled
				userID = defaultUserID
			}

			// Inject userID into the context
			ctx := context.WithValue(r.Context(), "userID", userID)
			next.ServeHTTP(w, r.WithContext(ctx))
		})
	}
}
