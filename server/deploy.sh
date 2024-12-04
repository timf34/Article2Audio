#!/bin/bash
set -e

# Pull the latest code
git pull origin main

# Build the Go binary
GOOS=linux GOARCH=amd64 go build -o article2audio-server cmd/api/main.go

# Build and deploy the container
podman build -t article2audio-server .
podman stop article2audio || true
podman rm article2audio || true
podman run -d --name article2audio -p 8080:8080 article2audio-server
