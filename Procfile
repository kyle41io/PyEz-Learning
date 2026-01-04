web: python manage.py migrate && python manage.py update_site_domain ${RENDER_EXTERNAL_HOSTNAME} && python manage.py collectstatic --noinput && gunicorn pyez_learning.wsgi --log-file -
