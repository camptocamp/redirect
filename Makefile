.PHONY: build
build:
	docker build --build-arg=GIT_HASH=$(shell git rev-parse HEAD) --tag=camptocamp/redirect .

.PHONY: lint
lint:
	docker build --target=lint .

