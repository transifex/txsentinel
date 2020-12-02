USER_ID = $$(id -u)
GROUP_ID = $$(id -g)

TAG = $$(git rev-parse --short HEAD)
TARGET = dev

build:
	docker build \
	--build-arg USER_ID=${USER_ID} \
	--build-arg GROUP_ID=${GROUP_ID} \
	-f ./Dockerfile \
	--target ${TARGET} \
	-t txsentinel:${TAG} . && \
	docker tag txsentinel:${TAG} txsentinel:latest

shell:
	docker-compose run --rm txsentinel-web bash

up:
	docker-compose up -d

down:
	docker-compose down

run-tests:
	docker-compose run --rm --entrypoint 'bash -c' txsentinel-web 'coverage run -m pytest && coverage report'
