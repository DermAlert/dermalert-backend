.PHONY: dev prod down

dev:
	docker compose -f docker-compose.dev.yml up --build

prod:
	docker compose -f docker-compose.prod.yml up --build -d

down:
	docker compose -f docker-compose.dev.yml -f docker-compose.prod.yml down
