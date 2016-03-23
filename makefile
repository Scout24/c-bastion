.PHONY: build run attach


# TODO this makes the assumption that there is exactly one container running.
attach:
	docker exec -it `docker ps | cut -f1 -d' ' | tail -1`  bash ; \
