package api

import (
	"article2audio/internal/auth"
	"context"
	"github.com/gorilla/mux"
	"net/http"
	"os"
	"strings"
)

func AuthMiddleware(authService *auth.Auth0Service) mux.MiddlewareFunc {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			if os.Getenv("ENABLE_AUTH") != "true" {
				// Use default user when auth is disabled
				ctx := context.WithValue(r.Context(), "userID", os.Getenv("DEFAULT_USER_ID"))
				next.ServeHTTP(w, r.WithContext(ctx))
				return
			}

			// Extract the token from the Authorization header
			authHeader := r.Header.Get("Authorization")
			if authHeader == "" {
				http.Error(w, "No authorization header", http.StatusUnauthorized)
				return
			}

			// Remove 'Bearer ' prefix
			tokenString := strings.TrimPrefix(authHeader, "Bearer ")

			// Validate the token
			userID, err := authService.ValidateToken(tokenString)
			if err != nil {
				http.Error(w, "Invalid token", http.StatusUnauthorized)
				return
			}

			// Add userID to context
			ctx := context.WithValue(r.Context(), "userID", userID)
			next.ServeHTTP(w, r.WithContext(ctx))
		})
	}
}
