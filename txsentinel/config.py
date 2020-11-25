import os


def get_secret(secret_name, default=""):
    """Will retrieve a secret trying file, enviroment and then settings in that
    order."""
    if 'SECRETS_PATH' in os.environ:
        filename = secret_name.replace('_', '-').lower()
        path = os.path.join(os.environ['SECRETS_PATH'], filename)
        try:
            with open(path, 'r') as f:
                return f.read()
        except IOError:
            pass
    return os.environ.get(secret_name, default)


CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND')


GITHUB_PR_REQUIRED_STATUS_CHECKS = [
    'continuous-integration/travis-ci/pr',
    'continuous-integration/jenkins/pr-merge'
]
GITHUB_ORGANIZATION = os.environ.get('GITHUB_ORGANIZATION')
GITHUB_USER = os.environ.get('GITHUB_USER')
GITHUB_DEPLOY_HEAD = os.environ.get('GITHUB_DEPLOY_HEAD')
GITHUB_DEPLOY_BASE = os.environ.get('GITHUB_DEPLOY_BASE', 'master')

GITHUB_STALE_BRANCH_DAYS = int(os.environ.get('GITHUB_STALE_BRANCH_DAYS', 90))
GITHUB_STALE_IGNORE_BRANCHES = os.environ.get(
    'GITHUB_STALE_IGNORE_BRANCHES',
    'master,base,devel'
).split(',')

GITHUB_TOKEN = get_secret('GITHUB_TOKEN', 'dev')
GITHUB_WEBHOOK_SECRET = get_secret('GITHUB_WEBHOOK_SECRET', 'dev')

SLACK_SIGNING_SECRET = get_secret('SLACK_SIGNING_SECRET', 'dev')

SECRET_KEY = get_secret('SECRET_KEY', 'dev')
