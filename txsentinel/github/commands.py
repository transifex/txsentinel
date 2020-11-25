import datetime
import click
from flask import current_app
from github import Github

from txsentinel import create_app
from txsentinel.github import cache


@current_app.cli.command("delete-stale-branches")
@click.option('--repo', default=None)
@click.option('--dry-run', is_flag=True)
def delete_stale_branches(dry_run, repo):
    now = datetime.datetime.now()
    git_client = Github(current_app.config['GITHUB_TOKEN'])
    git_org = git_client.get_organization(
        current_app.config['GITHUB_ORGANIZATION']
    )

    repositories = [git_org.get_repo(repo)] if repo else git_org.get_repos()
    for repo in repositories:
        if repo.archived or not repo.permissions.push:
            continue

        for branch in repo.get_branches():
            should_skip = (
                branch.protected or
                branch.name in current_app.config['GITHUB_STALE_IGNORE_BRANCHES']  # noqa
            )
            if should_skip:
                continue

            last_modified_dt = datetime.datetime.strptime(
                branch.commit.commit.last_modified,
                '%a, %d %b %Y  %H:%M:%S %Z'
            )
            is_stale = (
                now - last_modified_dt
            ).days > current_app.config['GITHUB_STALE_BRANCH_DAYS']

            if is_stale:
                print(
                    f'Deleting branch `{branch.name}` of repo `{repo.name}` '
                    f'with last modified date '
                    f'{branch.commit.commit.last_modified}'
                )
                if not dry_run:
                    git_ref = repo.get_git_ref(f'heads/{branch.name}')
                    git_ref.delete()
