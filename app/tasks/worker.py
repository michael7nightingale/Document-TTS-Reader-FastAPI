from celery import Celery

from app.core.config import get_app_settings


celery = Celery(__name__)
settings = get_app_settings()
celery.conf.broker_url = settings.CELERY_BROKER_URL
celery.conf.result_backend = settings.CELERY_RESULT_BACKEND
