# frontend/Dockerfile
FROM node:22-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy the rest of the frontend
COPY . .

# Expose Vite dev server port
EXPOSE 5173

# Run Vite dev server (for development)
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]
