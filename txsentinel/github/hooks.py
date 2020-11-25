from datetime import datetime

from flask import current_app, request
from github_webhook import Webhook

from txsentinel.github import cache
from txsentinel.github.tasks import maybe_merge

webhook = Webhook(
    current_app,
    secret=current_app.config['GITHUB_WEBHOOK_SECRET']
)


@webhook.hook(event_type='push')
def on_push(data):
    print('Got push with: {0}'.format(data))


@webhook.hook(event_type='pull_request_review')
def on_pull_request_review(data):
    if data['review']['state'].lower() != 'approved':
        return

    print('Got pull request review with: {0}'.format(data))

    maybe_merge.delay(
        data['repository']['full_name'],
        data['pull_request']['number']
    )


@webhook.hook(event_type='status')
def on_status(data):
    if data['state'] != 'success':
        return
    if data['context'] not in current_app.config['GITHUB_PR_REQUIRED_STATUS_CHECKS']:  # noqa
        return

    print('Got status with: {0}'.format(data))

    repo = cache.get_repository(data['repository']['full_name'])

    for branch in data['branches']:
        head = "{}:{}".format(
            current_app.config['GITHUB_ORGANIZATION'],
            branch['name']
        )
        for pull_request in repo.get_pulls(head=head):
            # Skip unmergeable PRs
            if pull_request.mergeable is False:
                continue

            maybe_merge.delay(
                data['repository']['full_name'],
                pull_request.number,
                git_hook_id=request.headers['X-GitHub-Delivery']
            )
