COMPOSE ?= docker compose
OUTPUT_DIR ?= ./output

.PHONY: build run up build-run rebuild down prepare-output

build:
	OUTPUT_DIR="$(OUTPUT_DIR)" $(COMPOSE) build

rebuild:
	OUTPUT_DIR="$(OUTPUT_DIR)" $(COMPOSE) build --no-cache

prepare-output:
	mkdir -p "$(OUTPUT_DIR)"

run: prepare-output
	-docker rm -f abb-scraper-run
	OUTPUT_DIR="$(OUTPUT_DIR)" $(COMPOSE) up scraper

down:
	-docker rm -f abb-scraper-run
	OUTPUT_DIR="$(OUTPUT_DIR)" $(COMPOSE) down -v

up: build run

build-run: build run
