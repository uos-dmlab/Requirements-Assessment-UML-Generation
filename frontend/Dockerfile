# ================================
# Multi-Stage Dockerfile for React/Vite Frontend
# ================================

# ============================================
# Stage 1: Build the React application
# ============================================
FROM node:18-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package.json only (not lock file - fixes rollup Alpine issue)
COPY app/package.json ./

# Install dependencies fresh for Alpine Linux
RUN npm install

# Copy application source code
COPY app/ ./

# Build the application
RUN npm run build

# ============================================
# Stage 2: Production-ready Nginx server
# ============================================
FROM nginx:alpine

# Install curl for healthcheck
RUN apk add --no-cache curl

# Remove default nginx static assets and configuration
RUN rm -rf /usr/share/nginx/html/* && \
    rm /etc/nginx/conf.d/default.conf

# Copy custom nginx configuration for SPA routing
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf

# Copy built application from builder stage
# Vite builds to 'dist' directory by default
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
