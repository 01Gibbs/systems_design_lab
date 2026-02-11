# Multi-stage build for production
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm ci

# Copy source
COPY . .

# Build
RUN npm run build

# Production stage
FROM node:20-alpine

WORKDIR /app

# Install serve for static files
RUN npm install -g serve

# Copy build files from builder
COPY --from=builder /app/dist ./dist

# Expose port
EXPOSE 5173

# Serve static files
CMD ["serve", "-s", "dist", "-l", "5173"]
