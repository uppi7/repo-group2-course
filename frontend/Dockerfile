# 多阶段构建
FROM node:20-alpine AS builder

WORKDIR /app
COPY package.json .
RUN npm install
COPY . .
RUN npm run build

# 仅承载静态文件的轻量镜像，无 CMD 进程
FROM alpine:3.19

WORKDIR /dist
COPY --from=builder /app/dist /dist
