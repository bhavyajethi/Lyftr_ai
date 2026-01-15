up:
	docker compose up -d --build

down:
	docker compose down -v

logs:
	docker compose logs -f api

test:
	# If you had tests, you would run them here
	echo "Running tests..."
	python -m unittest discover tests