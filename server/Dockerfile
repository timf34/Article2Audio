# Use a lightweight base image
FROM alpine:latest

# Install necessary packages
RUN apk --no-cache add ca-certificates

# Set working directory
WORKDIR /app

# Copy the compiled Go binary
COPY article2audio-server .

# Expose the application port
EXPOSE 8080

# Command to run the server
CMD ["./article2audio-server"]
