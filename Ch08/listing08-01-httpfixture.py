from concurrent.futures import ThreadPoolExecutor
import typing as t
import wsgiref.simple_server

import flask
import pytest

from apd.sensors.wsgi import v20
from apd.sensors.wsgi import set_up_config


def get_independent_flask_app(name: str) -> flask.Flask:
    """ Create a new flask app with the v20 API blueprint loaded, so multiple copies
    of the app can be run in parallel without conflicting configuration """
    app = flask.Flask(name)
    app.register_blueprint(v20.version, url_prefix="/v/2.0")
    return app


def run_server_in_thread(
    name: str, config: t.Dict[str, t.Any], port: int
) -> t.Iterator[str]:
    # Create a new flask app and load in required code, to prevent config conflicts
    app = get_independent_flask_app(name)
    flask_app = set_up_config(config, app)
    server = wsgiref.simple_server.make_server("localhost", port, flask_app)

    with ThreadPoolExecutor() as pool:
        pool.submit(server.serve_forever)
        yield f"http://localhost:{port}/"
        server.shutdown()


@pytest.fixture(scope="session")
def http_server():
    yield from run_server_in_thread(
        "standard", {"APD_SENSORS_API_KEY": "testing"}, 12081
    )


def test_http(http_server):
    import requests

    response = requests.get(http_server + "v/2.0/sensors")
    assert response.status_code == 403
