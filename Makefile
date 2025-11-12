manage = poetry run python src/manage.py

deps:
	poetry install --no-root

dev:
	docker-compose up --build --detach
	make for_dev
	
up:
	docker compose up -d

down:
	docker compose down && docker network prune --force

fmt:
	poetry run ruff format
	poetry run ruff check --fix --unsafe-fixes
	poetry run toml-sort pyproject.toml
	make fmt-gitignore

fmt-gitignore:
	sort --output .gitignore .gitignore
	awk "NF" .gitignore > .gitignore.temp && mv .gitignore.temp .gitignore

check:
	$(manage) makemigrations --check --dry-run --no-input
	$(manage) check
	poetry run ruff format --check
	poetry run ruff check --unsafe-fixes
	poetry run flake8 tests --select AAA
	poetry run toml-sort pyproject.toml --check

for_dev: fmt check test

clean:
	rm ~/.python_history

run:
	$(manage) migrate
	$(manage) runserver

test:
	poetry run pytest --create-db

