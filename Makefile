RUN=docker compose run --rm app
NONE_IMAGES=docker images -f "dangling=true" -q

all:
	docker compose build
	docker rmi $$(${NONE_IMAGES}) -f

run:
	docker compose up

migrate:
	${RUN} alembic upgrade head

revision:
	${RUN} alembic revision --autogenerate