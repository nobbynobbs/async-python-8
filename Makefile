.PHONY: tests

run-redis:
	docker-compose up -d

stop-redis:
	docker-compose down

tests:
	poetry run pytest tests -v --cov=async_python_8