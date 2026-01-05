.PHONY: help install test test-cov test-verbose lint format clean train check-api all

help:
	@echo "╔════════════════════════════════════════════════════════════╗"
	@echo "║              MLOps Development Commands                    ║"
	@echo "╚════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install              - Install all dependencies"
	@echo "  make install-dev          - Install dev dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  make test                 - Run all unit tests"
	@echo "  make test-cov             - Run tests with coverage report"
	@echo "  make test-verbose         - Run tests in verbose mode"
	@echo "  make test-fast            - Run tests without slow tests"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint                 - Run all linters (flake8, pylint)"
	@echo "  make format               - Format code with black & isort"
	@echo "  make format-check         - Check code format without changes"
	@echo ""
	@echo "Model Training:"
	@echo "  make train                - Train the ML model"
	@echo "  make train-verbose        - Train model with verbose output"
	@echo ""
	@echo "Development:"
	@echo "  make api-dev              - Run API in development mode"
	@echo "  make check-api            - Test API endpoints"
	@echo "  make mlflow               - Start MLflow UI"
	@echo ""
	@echo "Full Pipeline:"
	@echo "  make all                  - Run linting, tests, and training"
	@echo "  make ci                   - Run CI pipeline locally"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean                - Clean build artifacts and cache"
	@echo "  make clean-models         - Remove trained models"
	@echo ""

install:
	pip install --upgrade pip
	pip install -r deployment/requirements.txt

install-dev:
	pip install --upgrade pip
	pip install -r requirements-dev.txt

test:
	pytest tests/ -v --tb=short

test-cov:
	pytest tests/ -v --tb=short --cov=src --cov=deployment/app --cov-report=html --cov-report=term-missing
	@echo ""
	@echo "✅ Coverage report generated: htmlcov/index.html"

test-verbose:
	pytest tests/ -vv --tb=long --capture=no

test-fast:
	pytest tests/ -v -m "not slow" --tb=short

test-specific:
	@read -p "Enter test path (e.g., tests/test_model.py::TestModelCreation::test_random_forest_creation): " test_path; \
	pytest $$test_path -vv --tb=long

lint:
	@echo "🎯 Running Flake8..."
	flake8 src/ deployment/app/ --count --statistics
	@echo ""
	@echo "🔍 Running Pylint..."
	pylint src/train_pipeline.py deployment/app/main.py --disable=all --enable=E,F || true

format:
	@echo "🎨 Formatting code with black..."
	black src/ deployment/app/ tests/
	@echo ""
	@echo "📝 Sorting imports with isort..."
	isort src/ deployment/app/ tests/
	@echo "✅ Code formatted successfully"

format-check:
	@echo "🎨 Checking code format..."
	black --check src/ deployment/app/ tests/ || echo "Run 'make format' to fix"
	@echo ""
	@echo "📝 Checking import sorting..."
	isort --check-only src/ deployment/app/ tests/ || echo "Run 'make format' to fix"

train:
	@echo "🤖 Starting model training..."
	python src/train_pipeline.py
	@echo "✅ Model training complete"

train-verbose:
	@echo "🤖 Starting model training (verbose)..."
	python src/train_pipeline.py --verbose

api-dev:
	@echo "🚀 Starting API server..."
	cd deployment && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

check-api:
	@echo "🧪 Testing API endpoints..."
	@echo ""
	@echo "Test 1: GET /"
	curl -X GET http://localhost:8000/
	@echo ""
	@echo ""
	@echo "Test 2: POST /predict"
	curl -X POST http://localhost:8000/predict \
		-H "Content-Type: application/json" \
		-d '{"age":63,"sex":1,"cp":3,"trestbps":145,"chol":233,"fbs":1,"restecg":0,"thalach":150,"exang":0,"oldpeak":2.3,"slope":0,"ca":0,"thal":1}'
	@echo ""
	@echo ""
	@echo "✅ API tests complete"

mlflow:
	@echo "📊 Starting MLflow UI..."
	mlflow ui --host 0.0.0.0 --port 5000
	@echo "🌐 MLflow UI available at http://localhost:5000"

all: lint test-cov train
	@echo ""
	@echo "╔════════════════════════════════════════════════════════════╗"
	@echo "║              Full Pipeline Completed! ✅                   ║"
	@echo "╚════════════════════════════════════════════════════════════╝"

ci: clean install-dev lint test-cov
	@echo ""
	@echo "✅ CI pipeline complete"

clean:
	@echo "🧹 Cleaning up..."
	find . -type d -name __pycache__ -exec rm -rf {} + || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + || true
	find . -type d -name ".coverage" -exec rm -rf {} + || true
	find . -type d -name "htmlcov" -exec rm -rf {} + || true
	find . -type d -name ".egg-info" -exec rm -rf {} + || true
	find . -type d -name "dist" -exec rm -rf {} + || true
	find . -type d -name "build" -exec rm -rf {} + || true
	@echo "✅ Cleanup complete"

clean-models:
	@echo "🗑️  Removing trained models..."
	rm -f models/*.joblib
	@echo "✅ Models removed"

version:
	@echo "🔍 Checking versions..."
	@echo "Python: $$(python --version)"
	@echo "pip: $$(pip --version)"
	@echo "pytest: $$(pytest --version)"
	@echo "flake8: $$(flake8 --version)"

.DEFAULT_GOAL := help
