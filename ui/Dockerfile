# ui/Dockerfile
FROM node:18-alpine

WORKDIR /app
COPY package.json ./
COPY package-lock.json ./
RUN npm install

COPY . .
RUN npm run build

# Serve using a lightweight static server
RUN npm install -g serve
EXPOSE 3000
CMD ["serve", "-s", "build", "-l", "3000"]
