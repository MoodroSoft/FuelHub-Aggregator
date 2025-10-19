make:
	cat ./Makefile

build:
	docker build . -t backend -f ./Dockerfile

dc-up:
	docker-compose up -d;

build_and_up: build dc-up

dc-build:
	docker-compose up -d --build

dc-down:
	docker-compose down

dc-restart: dc-down dc-up

al-up:
	docker exec -it backend alembic upgrade head

al-new:
	docker exec -it backend alembic revision --autogenerate -m "$(message)"

al-down:
	docker exec -it backend alembic downgrade -1


pytest:
	docker exec -it backend bash -c 'cd ../tests; ENABLE_RATE_LIMITING=False SQL_DEBUG=False ENABLE_CACHE=False pytest -v $(test) --disable-warnings'

workers=8
pytest-xdist:
	docker exec -it backend  bash -c 'cd ../tests; ENABLE_RATE_LIMITING=False SQL_DEBUG=False ENABLE_CACHE=False pytest -vs --disable-warnings -n $(workers) $(test)'