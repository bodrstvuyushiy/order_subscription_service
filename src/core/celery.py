import logging
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

try:
    from celery import Celery
except ModuleNotFoundError:
    Celery = None
    logging.getLogger(__name__).warning()


class _DummyCelery:
    def config_from_object(self, *args, **kwargs):
        return None

    def autodiscover_tasks(self, *args, **kwargs):
        return None

    def task(self, *dargs, **dkwargs):
        def decorator(func):
            return func

        if dargs and callable(dargs[0]):
            return decorator(dargs[0])
        return decorator


if Celery is not None:
    app = Celery("core")
    app.config_from_object("django.conf:settings", namespace="CELERY")
    app.autodiscover_tasks()
else:
    app = _DummyCelery()
