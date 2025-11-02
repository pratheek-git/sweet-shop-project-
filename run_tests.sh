#!/bin/bash
# Run tests with coverage report

echo "Running backend tests..."
cd backend
pytest --cov=app --cov-report=html --cov-report=term
echo "Test coverage report generated in htmlcov/index.html"

