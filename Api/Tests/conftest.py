import pytest
import json
from Api.legacy_client import app


@pytest.fixture
def flask_app():
    flask_app = app
    flask_app.config.update({
        "TESTING": True
    })
    yield flask_app


@pytest.fixture
def client(flask_app):
    return flask_app.test_client()


@pytest.fixture
def runner(flask_app):
    return flask_app.test_cli_runner()
