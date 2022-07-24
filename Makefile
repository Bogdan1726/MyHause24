MANAGE = python myhause24/manage.py
SOURCE = myhause24

run:
	$(MANAGE) runserver

migrations:
	$(MANAGE) makemigrations

migrate:
	$(MANAGE) migrate

superuser:
	$(MANAGE) createsuperuser

# Docker
start_worker:
	cd $(SOURCE) && celery -A myhause24 worker -l info

start_app:
	$(MANAGE) migrate --no-input
	$(MANAGE) loaddata dump.json
#	$(MANAGE) collectstatic --no-input
	cd $(SOURCE) && gunicorn myhause24.wsgi:application -b 0.0.0.0:8000



#shell:
#	docker exec -it container_cinema python manage.py shell
#
#dump_data:
#	docker exec -it container_cinema python manage.py loaddata db.json