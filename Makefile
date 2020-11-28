GROUP_ID = $$(id -g)
USER_ID = $$(id -u)

TAG = $$(git rev-parse --short HEAD)
TARGET = dev

build:
	docker build \
		--build-arg USER_ID=${USER_ID} \
		--build-arg GROUP_ID=${GROUP_ID} \
		--target ${TARGET} \
		-f ./Dockerfile \
		-t txsentinel:${TAG} . && \
		docker tag txsentinel:${TAG} txsentinel:latest

up:
	docker-compose up -d

down:
	docker-compose down

shell:
	docker-compose run --rm txsentinel-web bash

run-tests:
	docker-compose run --rm --entrypoint 'bash -c' txsentinel-web 'coverage run -m pytest && coverage report'
