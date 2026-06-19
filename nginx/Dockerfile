FROM nginx:1.31-alpine

# Hapus default config
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom config
COPY nginx.conf /etc/nginx/conf.d/

# Health check endpoint
RUN apk add --no-cache curl

EXPOSE 80 8080

CMD ["nginx", "-g", "daemon off;"]