.PHONY: help
help: ## Display this help message
	@echo "Usage: make <target>"
	@echo
	@echo "Available targets:"
	@grep --extended-regexp --no-filename '^[a-zA-Z_-]+:.*## ' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "	%-20s%s\n", $$1, $$2}'

.PHONY: build
build: ## Build the image
	docker build --build-arg=GIT_HASH=$(shell git rev-parse HEAD) --tag=camptocamp/redirect .

.PHONY: build-dev
build-dev:  ## Build the image for development (Prospector and pytest)
	docker build --target=dev --build-arg=GIT_HASH=$(shell git rev-parse HEAD) --tag=camptocamp/redirect-dev .

.PHONY: lint
lint: build-dev  ## Lint the project with Prospector
	docker run --rm --volume=$(shell pwd)/redirect:/app/redirect camptocamp/redirect-dev prospector --output=pylint --die-on-tool-error .

.PHONY: run
run: build build-dev  ## Run the project to test it
	docker-compose up -d

.PHONY: tests
tests: run ## Run the acceptences tests
	docker-compose exec -T tests pytest --verbosity=2
