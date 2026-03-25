#!/bin/bash

# Run all tests
echo "Running all backend tests..."
cd "$(dirname "$0")"

# Install pytest if needed
pip install pytest pytest-cov -q

# Run tests with coverage
python -m pytest tests/ -v --cov=services --cov=memory --cov-report=term-missing

# Or run specific test files:
# python -m pytest tests/test_data_service.py -v
# python -m pytest tests/test_intent_classifier.py -v
# python -m pytest tests/test_chat_memory.py -v
# python -m pytest tests/test_ai_chat_service.py -v
# python -m pytest tests/test_api_chat.py -v

echo ""
echo "Test run complete!"
