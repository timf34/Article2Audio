# Server 

Using podman (background docker daemon uses too much memory) on our droplet for development.

```
podman build -t server .
podman run -d -p 8001:8001 server
```

To watch live logs:
```bash
podman logs -f <container-id>
```

Note: we can run the server on DO and still have our client running locally, just update the client/.env file 
to point to the DO server.