.PHONY: build run attach

all:
	make build
	pyb -X publish

# TODO this makes the assumption that there is exactly one container running.
attach:
	docker exec -it `docker ps | cut -f1 -d' ' | tail -1`  bash ; \

system-test:
	pyb -X run_cram_tests
