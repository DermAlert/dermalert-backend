.PHONY: dev prod down

dev:
	docker compose -f docker-compose.dev.yml up --build

prod:
	docker compose -f docker-compose.prod.yml up --build -d

down:
	docker compose -f docker-compose.dev.yml -f docker-compose.prod.yml down

test:
	docker compose -f docker-compose.dev.yml run --rm dermalert \
	  sh -c "uv sync --group test --locked && uv run pytest -ra -vv"

coverage:
	docker compose -f docker-compose.dev.yml run --rm dermalert \
	  sh -c 'uv sync --group test --locked && \
	         uv run pytest --cov --cov-report=term-missing'

lint:
	docker compose -f docker-compose.dev.yml run --rm dermalert \
	  sh -c "uv run ruff check ."