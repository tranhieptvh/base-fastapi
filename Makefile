build:
	docker compose build

up:
	sudo service apache2 stop
	docker compose up -d app db

down:
	docker compose down

restart:
	docker compose restart

exec:
	docker compose exec -it app bash

# Full cleanup
clean:
	docker compose down -v --rmi all

up-worker:
	docker compose up -d worker beat

down-worker:
	docker compose down worker beat

