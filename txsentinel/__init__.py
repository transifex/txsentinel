from flask import Flask, jsonify, request

from txsentinel.celery import celery_client
from txsentinel.slack.utils import validate_slack_hook
from txsentinel.slack.tasks import handle_deploy


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        app.config.from_object("txsentinel.config")
    else:
        app.config.from_mapping(test_config)

    celery_client.conf.update(app.config)

    # Health endpoint
    @app.route("/health")
    def health():
        return jsonify({"status": "ok"})

    # Liveness endpoint
    @app.route("/liveness")
    def liveness():
        import socket
        from kombu import Connection
        conn = Connection(app.config['CELERY_BROKER_URL'])
        conn.ensure_connection(
            interval_start=0.2,
            interval_step=0,
            max_retries=3
        )
        return jsonify({"status": "ok"})


    # Slack endpoints
    @app.route('/slack/hook', methods=['POST'])
    def on_hook():
        response = None
        content = request.get_json()
        if content.get('type') == 'url_verification':
            response = {'challenge': content.get('challenge')}
        elif content.get('type') == 'app_mention':
            print(content)
        return jsonify(response)

    @app.route('/slack/command', methods=['POST'])
    def on_command():
        validate_slack_hook(request)
        cmd_data = {
            'token': request.form.get('token'),
            'team_id': request.form.get('team_id'),
            'team_domain': request.form.get('team_domain'),
            'channel_id': request.form.get('channel_id'),
            'channel_name': request.form.get('channel_name'),
            'user_id': request.form.get('user_id'),
            'user_name': request.form.get('user_name'),
            'command': request.form.get('command'),
            'text': request.form.get('text'),
            'response_url': request.form.get('response_url'),
            'trigger_id': request.form.get('trigger_id'),
        }
        handle_deploy.delay(cmd_data)
        return jsonify({
            'response_type': 'in_channel',
            'text': 'Received deployment `{}`'.format(cmd_data['text'])
        })

    # Import the github hooks
    with app.app_context():
        from txsentinel.github import commands, hooks

    return app
