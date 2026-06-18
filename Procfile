web: python manage.py migrate --noinput && python manage.py setup_oauth && gunicorn codegreen.wsgi --workers 2 --bind 0.0.0.0:$PORT
