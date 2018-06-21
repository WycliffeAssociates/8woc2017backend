from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tRecorderApi.settings')
app = Celery(get_wsgi_application())

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# workaround for the setting CELERY_TASK_RESULT_EXPIRES which doesn't work
app.conf.result_expires = 604800  # store tasks results for 7 days (in seconds)
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
