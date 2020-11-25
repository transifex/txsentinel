from datetime import datetime

from txsentinel.celery import celery_client
from flask import current_app
from github import GithubException
from txsentinel.github import cache


@celery_client.task(bind=True)
def maybe_merge(self, repo_name, pull_request_number, git_hook_id=None):
    """Checks for the mergability of a PR and merges it if the checks pass."""
    repo = cache.get_repository(repo_name)
    pull_request = repo.get_pull(pull_request_number)

    # Mergeable status is still being calculated
    if pull_request.mergeable is None:
        self.retry(countdown=5)

    # Check if branch should be merged
    if not pull_request.mergeable:
        return

    labels = [label.name for label in pull_request.get_labels()]
    if 'auto-merge' not in labels:
        return

    deploy_base = current_app.config['GITHUB_DEPLOY_BASE']
    if pull_request.base.ref == deploy_base:
        tag = None
        for label in labels:
            if label.startswith('v:'):
                tag = label[2:]
                break
        if tag is None:
            raise Exception('No version tag found')

        deploy_base_ref = repo.get_git_ref(f'heads/{deploy_base}')
        deploy_base_ref.edit(pull_request.head.sha)

        repo.create_git_tag_and_release(
            tag, pull_request.body, pull_request.title, pull_request.body,
            pull_request.head.sha, 'commit'
        )
    else:
        try:
            pull_request.merge()
        except GithubException as e:
            print(git_hook_id)
            raise e
