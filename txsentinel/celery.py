from celery import Celery

from txsentinel.config import CELERY_BROKER_URL

celery_client = Celery('txsentinel', broker=CELERY_BROKER_URL)
