echo "Aplicando migraciones..."
python manage.py migrate --noinput

echo "Recopilando archivos estáticos..."
python manage.py collectstatic --noinput

echo "Arrancando Gunicorn..."
exec gunicorn DjangoApp.wsgi:application --bind 0.0.0.0:${PORT:-8000}