import logging
import os
import socket
import uuid

from flask import Flask
from flask_cors import CORS
from flask_log_request_id import RequestID, RequestIDLogFilter, \
    current_request_id
from werkzeug.contrib.fixers import ProxyFix

from web_crawler.apis import blueprint as si_simulator_apiv1
from web_crawler.apis.v1.app_settings import URL_PREFIX
from web_crawler.config import config_by_name


def register_blueprints(app):
    app.register_blueprint(si_simulator_apiv1,
                           url_prefix=URL_PREFIX)


class MachineInfoLogFilter(logging.Filter):
    def filter(self, log_record):
        log_record.machine_ip = socket.gethostname()
        log_record.env = os.getenv('FLASK_CONFIG') or 'dev'
        return log_record


def configure_logging(app):
    handler = logging.FileHandler(
        f'{app.config["LOGGING_DIR"]}/{app.config["LOGGING_FILE"]}')
    handler.setFormatter(logging.Formatter(
        '%(asctime)s [%(levelname)s] %(machine_ip)s %(env)s '
        '%(request_id)s %(name)s %(funcName)s:%(lineno)d %(message)s'))  # noqa
    handler.setLevel(getattr(logging, app.config["LOG_LEVEL"]))
    handler.addFilter(RequestIDLogFilter())
    handler.addFilter(MachineInfoLogFilter())
    app.logger.addHandler(handler)


def create_app():
    FLASK_CONFIG = os.getenv('FLASK_CONFIG') or 'dev'
    print(f'Loading {FLASK_CONFIG} configurations')

    app = Flask(__name__)
    RequestID(app,
              request_id_generator=lambda: f'simulation_rid{uuid.uuid4().hex}')

    app.secret_key = "l\x9b\x0cb\x86\x96Z/-\x88Ry\x03y\xea\x9c"

    app.config.from_object(config_by_name[FLASK_CONFIG])

    app.config.SWAGGER_UI_DOC_EXPANSION = 'list'
    app.config.SWAGGER_UI_OPERATION_ID = True
    app.config.SWAGGER_UI_REQUEST_DURATION = True

    app.wsgi_app = ProxyFix(app.wsgi_app)

    # register blueprints
    register_blueprints(app)

    configure_logging(app)

    # enable cors
    CORS(app)

    return app


app = create_app()


@app.after_request
def append_request_id(response):
    response.headers.add('X-REQUEST-ID', current_request_id())
    return response


@app.route('/crawler/health', methods=['GET'])
def health_check():
    return {'status': 'OK'}, 200
