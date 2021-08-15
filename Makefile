ENV ?= local

run:
	docker compose up --build --remove-orphans

test:
	docker compose \
	-f docker-compose-test.yml \
	up --build \
	--remove-orphans \
	--exit-code-from test-runner

