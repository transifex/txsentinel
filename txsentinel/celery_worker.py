import os

from txsentinel import create_app
from txsentinel.celery import celery_client

app = create_app()
app.app_context().push()
