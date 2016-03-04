.PHONY: build run attach

build:
	pyb clean
	pyb
	docker build -t cbastion:latest .

run: guard-AUTH_URL
	docker run -p 127.0.0.1:8080:8080 -e AUTH_URL=${AUTH_URL} cbastion:latest

# TODO this makes the assumption that there is exactly one container running.
attach:
	docker exec -it `docker ps | cut -f1 -d' ' | tail -1`  bash ; \

guard-%:
	@ if [ "${${*}}" = "" ]; then \
		echo "Environment variable $* not set"; \
		exit 1; \
	fi
