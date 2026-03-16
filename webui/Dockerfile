FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm install --registry=https://registry.npmmirror.com

COPY . .
RUN npx vite build

FROM nginx:alpine

RUN apk add --no-cache tzdata && \
    cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone && \
    apk del tzdata

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
