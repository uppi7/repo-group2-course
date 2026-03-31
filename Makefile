# repo-group2-course/Makefile
IMAGE_BACKEND  = zjuse-backend-course
IMAGE_FRONTEND = zjuse-frontend-course
TAG            = latest

.PHONY: dev dev-d logs down build build-backend build-frontend clean

dev:
	docker compose -f docker-compose.dev.yml --env-file .env up

dev-d:
	docker compose -f docker-compose.dev.yml --env-file .env up -d

down:
	docker compose -f docker-compose.dev.yml down

build-backend:
	docker build -t $(IMAGE_BACKEND):$(TAG) ./backend

build-frontend:
	docker build -t $(IMAGE_FRONTEND):$(TAG) ./frontend
	docker run --rm $(IMAGE_FRONTEND):$(TAG) ls /dist

build: build-backend build-frontend

clean:
	docker compose -f docker-compose.dev.yml down -v
