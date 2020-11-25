from flask import current_app
from github import Github

repositories = {}


def get_repository(repo_name):
    if repo_name in repositories:
        return repositories[repo_name]

    git_client = Github(current_app.config['GITHUB_TOKEN'])

    repo = git_client.get_repo(repo_name)
    repositories[repo_name] = repo
    return repo
