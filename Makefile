.PHONY: build_docker build_test test testall docs install pytest lab lint lint_docker

install:
	uv sync --group dev --group docs

pytest:
	uv run pytest tests/

lab:
	uv run jupyter lab lab/

build_docker:
	docker build -t chironpy-test .

test:
	docker-compose -f docker/docker-compose.test.yml build
	docker-compose -f docker/docker-compose.test.yml run chironpy tox ${toxargs} -- ${pytestargs}

lint:
	uv run ruff format chironpy/ tests/ examples/
	uv run ruff check chironpy/ tests/ examples/

lint_docker:
	docker-compose -f docker/docker-compose.lint.yml build
	docker-compose -f docker/docker-compose.lint.yml run chironpy

testall:
	docker-compose -f docker/docker-compose.test.yml build
	docker-compose -f docker/docker-compose.test.yml run chironpy

docs:
	cp CONTRIBUTING.md docs/CONTRIBUTING.md
	docker-compose -f docker/docker-compose.docs.yml up --remove-orphans

build_docs:
	docker-compose -f docker/docker-compose.docs.yml build
