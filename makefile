.PHONY: build run attach

all:
	make build
	pyb -X publish

build:
	pyb -X clean
	pyb -X package
	docker build -t c-bastion .

run: guard-AUTH_URL
	docker run -p 127.0.0.1:8080:8080 -e AUTH_URL=${AUTH_URL} c-bastion:latest

# TODO this makes the assumption that there is exactly one container running.
attach:
	docker exec -it `docker ps | cut -f1 -d' ' | tail -1`  bash ; \

system-test:
	pyb -X run_cram_tests

guard-%:
	@ if [ "${${*}}" = "" ]; then \
		echo "Environment variable $* not set"; \
		exit 1; \
	fi
