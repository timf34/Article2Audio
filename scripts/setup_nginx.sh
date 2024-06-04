#!/bin/bash

# Variables
DOMAIN="article2audio.com"
WWW_DOMAIN="www.article2audio.com"
FRONTEND_PORT=3000
BACKEND_PORT=8001

# Update and install Nginx
apt update
apt install -y nginx

# Configure the firewall to allow Nginx traffic
ufw allow 'Nginx Full'
ufw reload

# Create Nginx configuration file
cat <<EOF > /etc/nginx/sites-available/$DOMAIN
server {
    listen 80;
    server_name $DOMAIN $WWW_DOMAIN;
    return 301 https://\$host\$request_uri;
}

server {
    listen 443 ssl;
    server_name $DOMAIN $WWW_DOMAIN;

    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;

    location / {
        proxy_pass http://localhost:$FRONTEND_PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /api/ {
        proxy_pass http://localhost:$BACKEND_PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable the Nginx configuration
ln -sf /etc/nginx/sites-available/$DOMAIN /etc/nginx/sites-enabled/

# Test the Nginx configuration
nginx -t

# Restart Nginx
systemctl restart nginx

# Install Certbot
apt install -y certbot python3-certbot-nginx

# Obtain an SSL certificate
certbot --nginx -d $DOMAIN -d $WWW_DOMAIN

echo "Setup completed successfully!"
