.PHONY: build_docker build_test test testall docs

build_docker:
	docker build -t chironpy-test .

test:
	docker-compose -f docker/docker-compose.test.yml build
	docker-compose -f docker/docker-compose.test.yml run chironpy tox ${toxargs} -- ${pytestargs}

lint:
	docker-compose -f docker/docker-compose.lint.yml build
	docker-compose -f docker/docker-compose.lint.yml run chironpy

testall:
	docker-compose -f docker/docker-compose.test.yml build
	docker-compose -f docker/docker-compose.test.yml run chironpy

docs:
	docker-compose -f docker/docker-compose.docs.yml up --remove-orphans

build_docs:
	docker-compose -f docker/docker-compose.docs.yml build
