from datetime import datetime
import time
import hmac
import hashlib

from flask import jsonify, current_app
from github import UnknownObjectException


class SlackException(Exception):
    status_code = 500


class BadArgumentsException(SlackException):
    status_code = 400


class BadSignatureException(SlackException):
    status_code = 400


class UknnownVersionSchemaException(Exception):
    status_code = 400


def handle_command_exc(e):
    return jsonify(e.msg_dict), e.status_code


def validate_slack_hook(request):
    """Validates wether a hook is originating from slack or not"""
    timestamp = request.headers['X-Slack-Request-Timestamp']
    if int(time.time()) - int(timestamp) > 60 * 5:
        raise BadSignatureException("Bad timestamp")

    slack_signing_secret = current_app.config['SLACK_SIGNING_SECRET']
    sig_basestring = ''.join([
        'v0:', timestamp, ':', request.get_data().decode()
    ])

    calculated_sig = 'v0=' + hmac.new(
        slack_signing_secret.encode(),
        msg=sig_basestring.encode(),
        digestmod=hashlib.sha256
    ).hexdigest()

    slack_sig = request.headers['X-Slack-Signature']

    if not calculated_sig == slack_sig:
        raise BadSignatureException("Bad signature")
    return


def validate_deploy_data(cmd_data):
    """Validates and returns the arguments passed with the deploy command."""
    cmd_args = {}
    text = cmd_data['text'].strip()

    for part in text.split():
        if not part:
            continue
        elif '=' in part:
            arg, value = part.split('=')
            cmd_args[arg] = value
        elif '--' in part:
            arg = part.replace('--', '')
            cmd_args[arg] = True
        else:
            raise BadArgumentsException("Cannot recognize argument")

    if 'repo' not in cmd_args:
        raise BadArgumentsException("Should specify repository.")

    default_args = {
        'env': 'prod',
        'head': current_app.config['GITHUB_DEPLOY_HEAD'],
        'tag': None,
        'dry-run': False,
    }
    final_args = cmd_args

    for arg, value in default_args.items():
        if arg not in final_args:
            final_args[arg] = value

    return final_args


def is_valid_tag(tag_name):
    """Validates a user provides tag."""
    try:
        datetime.strptime(tag_name, '%Y%m%d-%H%M')
        return True
    except ValueError:
        pass

    tag_parts = tag_name.split('.')
    if len(tag_parts) == 3:
        return True

    return False


def get_tag(repo):
    """Creates and returns the next release tag."""

    try:
        last_release = repo.get_latest_release()
    except UnknownObjectException:
        return '0.0.1'

    tag_name = last_release.tag_name

    # Test if tag is in date format
    try:
        datetime.strptime(tag_name, '%Y%m%d-%H%M')
    except ValueError:
        pass
    else:
        return datetime.now().strftime('%Y%m%d-%H%M')

    tag_parts = tag_name.split('.')
    if len(tag_parts) == 3:
        return '.'.join([
            tag_parts[0],
            tag_parts[1],
            str(int(tag_parts[2]) + 1)
        ])

    raise UknnownVersionSchemaException(
        f'The tag `{tag_name}` is not conforming to any known schema.'
    )
