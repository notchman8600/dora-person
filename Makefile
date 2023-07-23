MODE=dev
pre:

ifdef mode
MODE=${mode}
endif

# develop mode
ifeq ($(MODE),dev)
	export COMPOSE_FILE=compose.yml;
endif

# production mode
ifeq ($(MODE),prod)
set-env := export MODE=$(MODE) ;\
	export COMPOSE_PATH_SEPARATOR=: ;\
	export COMPOSE_FILE=compose.$(MODE).yml;
endif

up: pre
	$(set-env)\
	docker compose up

upd: pre
	$(set-env)\
	docker compose up -d

down: pre
	$(set-env)\
	docker compose down

rebuild: pre
	$(set-env)\
	docker compose build --no-cache

build: pre
	$(set-env) \
	docker compose build

ps: pre
	$(set-env) \
	docker compose ps

config: pre
	$(set-env)\
	docker compose config

reset: pre
	$(set-env)\
	docker compose down --rmi all --volumes --remove-orphans