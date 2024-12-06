package auth

import (
	"crypto/rsa"
	"encoding/base64"
	"encoding/json"
	"errors"
	"fmt"
	"github.com/golang-jwt/jwt/v5"
	"log"
	"math/big"
	"net/http"
	"os"
	"sync"
	"time"
)

type Auth0Service struct {
	issuer    string
	audience  string
	jwksURL   string
	keys      map[string]*rsa.PublicKey
	keysLock  sync.RWMutex
	lastFetch time.Time
}

func New() *Auth0Service {
	domain := os.Getenv("AUTH0_DOMAIN")
	return &Auth0Service{
		issuer:   fmt.Sprintf("https://%s/", domain),
		audience: os.Getenv("AUTH0_AUDIENCE"),
		jwksURL:  fmt.Sprintf("https://%s/.well-known/jwks.json", domain),
		keys:     make(map[string]*rsa.PublicKey),
	}
}

type JWKS struct {
	Keys []JSONWebKey `json:"keys"`
}

type JSONWebKey struct {
	Kid string `json:"kid"`
	Kty string `json:"kty"`
	N   string `json:"n"`
	E   string `json:"e"`
}

func (s *Auth0Service) getSigningKey(token *jwt.Token) (interface{}, error) {
	kid, ok := token.Header["kid"].(string)
	if !ok {
		return nil, errors.New("invalid key ID")
	}

	// Check if we have the key cached
	s.keysLock.RLock()
	if key, exists := s.keys[kid]; exists {
		s.keysLock.RUnlock()
		return key, nil
	}
	s.keysLock.RUnlock()

	// Fetch new keys
	if err := s.fetchKeys(); err != nil {
		return nil, fmt.Errorf("error fetching keys: %v", err)
	}

	// Try again with new keys
	s.keysLock.RLock()
	key, exists := s.keys[kid]
	s.keysLock.RUnlock()

	if !exists {
		return nil, errors.New("unable to find appropriate key")
	}

	return key, nil
}

func (s *Auth0Service) fetchKeys() error {
	resp, err := http.Get(s.jwksURL)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	var jwks JWKS
	if err := json.NewDecoder(resp.Body).Decode(&jwks); err != nil {
		return err
	}

	newKeys := make(map[string]*rsa.PublicKey)
	for _, key := range jwks.Keys {
		if key.Kty != "RSA" {
			continue
		}

		// Decode the modulus
		nBytes, err := base64.RawURLEncoding.DecodeString(key.N)
		if err != nil {
			continue
		}
		n := new(big.Int).SetBytes(nBytes)

		// Decode the exponent
		eBytes, err := base64.RawURLEncoding.DecodeString(key.E)
		if err != nil {
			continue
		}
		e := new(big.Int).SetBytes(eBytes)

		newKeys[key.Kid] = &rsa.PublicKey{
			N: n,
			E: int(e.Int64()),
		}
	}

	s.keysLock.Lock()
	s.keys = newKeys
	s.lastFetch = time.Now()
	s.keysLock.Unlock()

	return nil
}

func (s *Auth0Service) ValidateToken(tokenString string) (string, error) {
	token, err := jwt.Parse(tokenString, func(token *jwt.Token) (interface{}, error) {
		// Verify signing method
		if _, ok := token.Method.(*jwt.SigningMethodRSA); !ok {
			errMsg := fmt.Sprintf("Unexpected signing method: %v", token.Header["alg"])
			log.Println(errMsg)
			return nil, fmt.Errorf(errMsg)
		}
		return s.getSigningKey(token)
	})

	if err != nil {
		log.Printf("Failed to parse token: %v", err)
		log.Printf("Token: %s", token)
		return "", fmt.Errorf("failed to parse token: %v", err)
	}

	claims, ok := token.Claims.(jwt.MapClaims)
	if !ok || !token.Valid {
		log.Println("Invalid token: claims not valid")
		return "", errors.New("invalid token")
	}

	// Validate issuer
	if iss, ok := claims["iss"].(string); !ok || iss != s.issuer {
		log.Printf("Invalid issuer: expected %s, got %s", s.issuer, iss)
		return "", errors.New("invalid issuer")
	}

	// Validate audience
	// Validate audience (allow multiple audiences)
	audClaim, ok := claims["aud"].([]interface{}) // Handle as an array
	if !ok {
		singleAud, ok := claims["aud"].(string) // Handle single audience case
		if !ok || singleAud != s.audience {
			return "", fmt.Errorf("invalid audience: expected %s, got %v", s.audience, claims["aud"])
		}
	} else {
		audienceValid := false
		for _, aud := range audClaim {
			if aud == s.audience {
				audienceValid = true
				break
			}
		}
		if !audienceValid {
			return "", fmt.Errorf("invalid audience: expected %s, got %v", s.audience, audClaim)
		}
	}

	// Get the subject (user ID)
	sub, ok := claims["sub"].(string)
	if !ok {
		log.Println("Missing 'sub' claim in token")
		return "", errors.New("missing sub claim")
	}

	return sub, nil
}
