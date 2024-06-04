# client/Dockerfile

# Stage 1: Build the React app
FROM node:14 AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Stage 2: Serve the React app using Nginx
FROM nginx:alpine

# Copy the build output to the Nginx html directory
COPY --from=build /app/build /usr/share/nginx/html

# Ensure the favicon.ico is correctly copied
COPY --from=build /app/public/favicon.ico /usr/share/nginx/html/favicon.ico

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
