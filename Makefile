USER_ID=$$(id -u)
GROUP_ID=$$(id -g)

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

up:
	docker-compose up

down:
	docker-compose down

shell:
	docker-compose run --rm txsentinel-web bash

run-tests:
	docker-compose run --rm --entrypoint 'bash -c' txsentinel-web 'coverage run -m pytest && coverage report'

helm_debug:
	helm install \
		--dry-run \
		--debug \
		--generate-name \
		-f helm/values_common.in.yaml \
		--set-string version=${TAG} \
		./helm/txsentinel

helm_install:
	helm upgrade \
		--install \
		--atomic \
		-f ./helm/values_common.yaml \
		--namespace dl-txsentinel \
		dl-txsentinel \
		./helm/txsentinel

ecr_login:
	eval $$(aws ecr get-login --region eu-west-1 --no-include-email)

ecr_push:
	docker tag txsentinel:${TAG} 775662142440.dkr.ecr.eu-west-1.amazonaws.com/devops-league:${TAG} && \
	docker push 775662142440.dkr.ecr.eu-west-1.amazonaws.com/devops-league:${TAG}
