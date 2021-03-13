import os

from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FundooApp.settings')

app = Celery('FundooApp')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.

app.conf.beat_schedule = {
    'every-15-seconds': {
        'task': 'authentication.utils.send_reminder_email',
        'schedule': 30,
        'args': ('amitksms97@gmail.com',)
    }
}

app.conf.timezone = 'UTC'

app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
