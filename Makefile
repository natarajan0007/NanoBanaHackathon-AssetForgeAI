.PHONY: help install dev test clean docker-build docker-up docker-down worker monitor

help:
	@echo "Available commands:"
	@echo "  install     - Install dependencies"
	@echo "  dev         - Start development server"
	@echo "  test        - Run tests"
	@echo "  clean       - Clean up temporary files"
	@echo "  docker-build - Build Docker images"
	@echo "  docker-up   - Start all services with Docker"
	@echo "  docker-down - Stop all Docker services"
	@echo "  worker      - Start Celery worker"
	@echo "  monitor     - Monitor Celery workers"

install:
	pip install -r backend-fast/requirements.txt

dev:
	uvicorn backend-fast.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest backend-fast/tests/ -v

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache
	rm -f backend-fast/celerybeat-schedule
	rm -f backend-fast/celerybeat.pid

docker-build:
	docker-compose -f docker-compose.yml build

docker-up:
	docker-compose -f docker-compose.yml up -d --build

docker-down:
	docker-compose -f docker-compose.yml down

worker:
	python backend-fast/scripts/start_worker.py --queue default --concurrency 2

worker-asset:
	python backend-fast/scripts/start_worker.py --queue asset_processing --concurrency 2

worker-generation:
	python backend-fast/scripts/start_worker.py --queue generation --concurrency 1

monitor:
	python backend-fast/scripts/monitor_celery.py --monitor

flower:
	celery -A backend-fast.app.celery_app flower --port=5555
