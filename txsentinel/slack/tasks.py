from txsentinel.celery import celery_client
from flask import current_app
from github import Github, GithubException
import requests

from txsentinel.github import cache
from txsentinel.slack.utils import validate_deploy_data, get_tag, is_valid_tag


def create_pr_body(prs_merged, migration_files):
    body = 'Merged Pull Requests:\n'
    body += '\n'.join([
        f"#{pr['number']} : {pr['title']}" for pr in prs_merged
    ])

    if migration_files:
        body += '\n\nMigrations altered:\n'
        body += '\n'.join([
            f'*{file}' for file in migration_files
        ])

    return body


def create_slack_body(prs_merged, migration_files):
    body = '*Merged Pull Requests:*\n\n'
    body += '\n'.join([
        f'<{pr["html_url"]}|#{pr["number"]}>: {pr["title"]}'
        for pr in prs_merged
    ])

    if migration_files:
        body += '\n *Migrations altered:* \n\n'
        body += '\n'.join([
            f'*{file}' for file in migration_files
        ])

    return body


@celery_client.task
def handle_deploy(cmd_data):
    """Handles the deploy command

    :param cmd_data: A dictionary containing the command data
    """
    cmd_args = validate_deploy_data(cmd_data)

    repo_name = ''.join([
        current_app.config['GITHUB_ORGANIZATION'],
        '/',
        cmd_args['repo']
    ])
    repo = cache.get_repository(repo_name)

    if cmd_args['env'] == 'prod':
        if cmd_args['tag'] is None:
            tag = get_tag(repo)
        elif is_valid_tag(cmd_args['tag']):
            tag = cmd_args['tag']
        else:
            raise Exception('No valid tag was provided')

        head = current_app.config['GITHUB_DEPLOY_HEAD']
        base = current_app.config['GITHUB_DEPLOY_BASE']
        comparison = repo.compare(base, head)

        prs_merged = []
        for commit in comparison.commits:
            if len(commit.parents) < 2:
                # Searching for merge commits
                # Merge commits have 2 parents (except fast forward)
                continue
            for pr in commit.get_pulls():
                prs_merged.append({
                    'number': pr.number,
                    'html_url': pr.html_url,
                    'title': pr.title
                })

        migration_files = []
        for changed_file in comparison.files:
            if 'migration' in changed_file.filename:
                migration_files.append(
                    changed_file.filename
                )

        title = f'Release: {tag}'

        if not prs_merged:
            data = {
                'response_type': 'in_channel',
                "blocks": [
                    {
                        "type": "image",
                        "title": {
                            "type": "plain_text",
                            "text": "Nothing to see here. Move along"
                        },
                        "block_id": "nothing_to_see",
                        "image_url": "https://evolutionnews.org/wp-content/uploads/2017/07/Nothing-to-See-Here.jpg",
                        "alt_text": "Move along."
                    }
                ]
            }
        elif cmd_args['dry-run']:
            body = create_slack_body(prs_merged, migration_files)
            data = {
                'response_type': 'in_channel',
                'text':
                    f'Pending new Release for `{repo.full_name}`: `{title}`.\n' +  # noqa
                    f'{body}'
            }
        else:
            body = create_pr_body(prs_merged, migration_files)
            try:
                pull_request = repo.create_pull(
                    title=title,
                    body=body,
                    base=base,
                    head=head
                )
            except GithubException as e:
                data = {
                    'response_type': 'in_channel',
                    'text':
                        f'PR creation failed for {repo.full_name}. ' +
                        e.data['errors'][0]['message']
                }
            else:
                pull_request.add_to_labels(
                    'auto-merge', f'v:{tag}'
                )
                data = {
                    'response_type': 'in_channel',
                    'text':
                        f'Created a pull request `{title}` for {repo.full_name}.\n' +  # noqa
                        f'Review the PR <{pull_request.html_url}|here.>'
                }
        requests.post(cmd_data['response_url'], json=data)
