package api

import (
	"context"
	"net/http"
	"os"
)

func UserAuthMiddleware(next http.Handler) http.Handler {
	enableAuth := os.Getenv("ENABLE_AUTH") == "true"
	defaultUserID := os.Getenv("DEFAULT_USER_ID")

	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		var userID string

		if enableAuth {
			// Here, you'd add real authentication logic (e.g., checking a token or session)
			// For now, simulate with a placeholder:
			userID = r.Header.Get("X-User-ID")
			if userID == "" {
				http.Error(w, "Unauthorized: No User ID provided", http.StatusUnauthorized)
				return
			}
		} else {
			// Use default user ID when authentication is disabled
			userID = defaultUserID
		}

		// Inject userID into the context
		ctx := context.WithValue(r.Context(), "userID", userID)
		next.ServeHTTP(w, r.WithContext(ctx))
	})
}
