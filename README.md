# tx-sentinel
> Application to oversee organization repositories and deployments (to rule them all)


## Installation
### Add to a repository
To have txsentinel watch over a repository you must add the following webhook in the github (repositoty) settings:

`https://sentinel.svc.transifex.net/postreceive`

To find the "Secret" contact the devops team.

And enable the sending of the following events:
* Pull requests
* Pull request reviews
* Pushes
* Statuses

## How to use

### auto-merge
Add the `auto-merge` label to you PR.

When ***all*** merge requirements are met txsentinel will merge the PR automatically.

### /deploy
The deploy slash command is available in the `releng` channel

`/deploy repo=tx-sentinel [tag=0.0.1]`


| Argument | Description | Default |
| --- | --- | --- |
| repo={repository_name} | The repository to deploy. | ***Required*** |
| tag={tag} | The tag to use when tagging and releasing. Valid tags are of the following formats: `X.Y.Z` & `YYYYMMDD-HHMM` . | Detects and generates the next valid tag. The tag `0.0.1` is used if no release is detected. |
| --dry-run | If this flag is set no PRs will be created and the preview of the Release will be reported back to slack | False

### flask delete-stale-branches
This flask command will, as you can already tell, delete the stale branches you have on github.
A stale branch is a branch that has not been modified for 90 days.

| Argument | Description |
| --- | --- |
| --repo {repository_name} | The repository to delete stale branches from |
| --dry-run | Print out the branch deletions but do not actually delete |

A comma separeted list of branches to ignore when checking for stale status can be provided via the
`GITHUB_STALE_IGNORE_BRANCHES` environment variable. It defaults to `master,base,devel`.

## Development

To begin development on this repository you must first clone it localy:

`git clone git@github.com:transifex/tx-sentinel.git`

And apply the fixes / features you wish.
