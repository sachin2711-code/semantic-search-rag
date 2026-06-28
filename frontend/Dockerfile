# Stage 1: compile the React app into plain static files
FROM node:20-alpine AS build

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY . .

# Baked in at BUILD time, not runtime — once nginx is serving plain HTML/JS,
# there's no environment to read from anymore. Override this default if you
# later deploy the backend somewhere other than localhost.
ARG VITE_API_BASE=http://localhost:8000
ENV VITE_API_BASE=$VITE_API_BASE

RUN npm run build

# Stage 2: serve the compiled output with a small, fast web server.
# Starting fresh from nginx here (not reusing the Node image) means the final
# image doesn't carry Node.js, node_modules, or any build tooling — just the
# finished static files.
FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
