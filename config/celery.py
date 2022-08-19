import os

from dotenv import load_dotenv

load_dotenv()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
os.environ.setdefault("DJANGO_CONFIGURATION", "Dev")

from configurations import importer  # noqa

importer.install(check_options=True)

from django.conf import settings  # noqa

from celery import Celery  # noqa

app = Celery("fcdocs_annotate")
app.config_from_object("django.conf:settings", namespace="CELERY", force=True)

app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
