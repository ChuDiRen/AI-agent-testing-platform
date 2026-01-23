.PHONY: help install install-dev run-backend run-frontend dev clean test lint format docker-build docker-run

help:
	@echo "Cyberpunk - API Automation Agent Platform"
	@echo ""
	@echo "Available commands:"
	@echo "  make install        - Install backend dependencies"
	@echo "  make install-dev    - Install backend and frontend dependencies"
	@echo "  make run-backend    - Run backend server"
	@echo "  make run-frontend   - Run frontend dev server"
	@echo "  make dev            - Run both backend and frontend"
	@echo "  make clean          - Clean build artifacts"
	@echo "  make test           - Run tests"
	@echo "  make lint           - Run linters"
	@echo "  make format         - Format code"
	@echo "  make docker-build   - Build Docker image"
	@echo "  make docker-run     - Run Docker container"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	cd web && pnpm install

run-backend:
	python run.py

run-frontend:
	cd web && pnpm dev

dev:
	@echo "Starting backend and frontend..."
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:5173"
	@make -j2 run-backend run-frontend

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf web/dist
	rm -rf web/node_modules/.vite

test:
	pytest

lint:
	ruff check app/
	cd web && pnpm lint

format:
	black app/
	ruff check --fix app/

docker-build:
	docker build -t cyberpunk:latest .

docker-run:
	docker run -d --name cyberpunk -p 8000:8000 cyberpunk:latest
