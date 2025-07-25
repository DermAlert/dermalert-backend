.PHONY: dev prod down setup-db migrate shell docs docs-build docs-deploy docs-clean

# Desenvolvimento
dev:
	docker compose -f docker-compose.dev.yml up --remove-orphans

build-dev:
	docker compose -f docker-compose.dev.yml --build

# Produção
prod:
	docker compose up --build -d --remove-orphans

# Parar todos os serviços
down:
	docker compose -f docker-compose.dev.yml down
	docker compose down

# Configurar banco de dados (desenvolvimento)
setup-db:
	docker compose -f docker-compose.dev.yml exec dermalert \
	    uv run manage.py migrate
	docker compose -f docker-compose.dev.yml exec dermalert \
	    uv run manage.py setup_minio
	docker compose -f docker-compose.dev.yml exec dermalert \
	    uv run manage.py collectstatic --noinput

# Executar migrações
migrate:
	docker compose -f docker-compose.dev.yml exec dermalert uv run manage.py migrate

# Shell do Django
shell:
	docker compose -f docker-compose.dev.yml exec dermalert uv run manage.py shell

# Conectar ao PostgreSQL
db-shell:
	docker compose -f docker-compose.dev.yml exec postgres psql -U django_user -d django_db

test:
	docker compose -f docker-compose.dev.yml run --rm --remove-orphans dermalert \
	  sh -c "uv sync --group test --locked && uv run pytest -ra -vv"

coverage:
	docker compose -f docker-compose.dev.yml run --rm --remove-orphans dermalert \
	  sh -c 'uv sync --group test --locked && \
	         uv run pytest --cov --cov-report=term-missing'

lint:
	docker compose -f docker-compose.dev.yml run --rm --remove-orphans dermalert \
	  sh -c "uv run ruff check ."

seed:
	docker compose -f docker-compose.dev.yml run --rm --remove-orphans dermalert \
	  sh -c "uv sync --group seed --locked && uv run uv run manage.py migrate && uv run uv run manage.py seed_all"

seed-clear:
	docker compose -f docker-compose.dev.yml run --rm --remove-orphans dermalert \
	  sh -c "uv run uv run manage.py seed_all --clear"

seed-list:
	docker compose -f docker-compose.dev.yml run --rm --remove-orphans dermalert \
	  sh -c "uv run uv run manage.py seed_all --list"

seed-basic:
	docker compose -f docker-compose.dev.yml run --rm --remove-orphans dermalert \
	  sh -c "uv run uv run manage.py seed_all --only seed_addresses seed_health_units"

seed-minimal:
	docker compose -f docker-compose.dev.yml run --rm --remove-orphans dermalert \
	  sh -c "uv run uv run manage.py seed_all --clear --users 5 --addresses 10 --health-units 2"

# Seed local (sem Docker)
seed-local:
	uv run manage.py migrate && uv run manage.py seed_all

seed-local-clear:
	uv run manage.py seed_all --clear

seed-local-list:
	uv run manage.py seed_all --list

seed-local-minimal:
	uv run manage.py seed_all --clear --users 5 --addresses 10 --health-units 2

# Script de seeds utilitário
seed-setup:
	./seeds.sh setup

seed-reset:
	./seeds.sh reset

seed-status:
	./seeds.sh status

# Documentação com MkDocs
docs:
	uv sync --group docs --locked && uv run mkdocs serve --dev-addr 127.0.0.1:8001

docs-build:
	uv sync --group docs --locked && uv run mkdocs build

docs-deploy:
	uv sync --group docs --locked && uv run mkdocs gh-deploy

docs-clean:
	rm -rf site/