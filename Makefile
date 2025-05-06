build:
	docker compose build --no-cache

up:
	sudo service apache2 stop
	docker compose up -d

down:
	docker compose down

restart:
	docker compose restart

exec:
	docker compose exec -it api bash

# Full cleanup
clean:
	docker compose down -v --rmi all

