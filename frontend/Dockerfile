FROM node:20-alpine AS base

WORKDIR /app

# Install deps first for better layer caching
COPY package.json ./
RUN npm install

COPY . .

# Security: run as non-root (node image ships a "node" user)
RUN chown -R node:node /app
USER node

EXPOSE 3000

ENV NEXT_TELEMETRY_DISABLED=1

CMD ["npm", "run", "dev"]
