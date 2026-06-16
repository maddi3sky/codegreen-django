web: gunicorn codegreen.wsgi --workers 2 --bind 0.0.0.0:$PORT
release: python manage.py migrate --run-syncdb && python manage.py collectstatic --noinput && python manage.py setup_oauth
