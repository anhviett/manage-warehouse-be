FROM node:20-alpine

WORKDIR /app

COPY package*.json ./

# Install tools needed to compile native packages
RUN apk add --no-cache python3 make g++ && \
    npm install && \
    apk del python3 make g++

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host"]
