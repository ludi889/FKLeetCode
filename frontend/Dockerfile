FROM node:22-alpine AS devel

WORKDIR /app

# Copy package management specs first for caching benefits
COPY package*.json ./

RUN npm install

# Copy application source code
COPY . .

EXPOSE 5173

# Run in development mode with host exposure enabled
CMD ["npm", "run", "dev", "--", "--host"]