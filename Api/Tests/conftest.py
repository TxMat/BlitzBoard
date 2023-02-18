import peewee
import pytest
import json
from Api.client import app, Player, Game, Score, Config, PlayerGame


# This is a fixture that will be used by all tests

# flask fixture
@pytest.fixture
def flask_app(db):
    flask_app = app
    flask_app.config.update({
        "TESTING": True,
        "DATABASE": db,
    })
    yield flask_app


# client fixture
@pytest.fixture
def client(flask_app):
    return flask_app.test_client()


# runner fixture
@pytest.fixture
def runner(flask_app):
    return flask_app.test_cli_runner()


# peewee fixture
@pytest.fixture(scope="session")
def db():
    db = peewee.SqliteDatabase('test.db')
    db.connect()
    db.create_tables([Game, Player, Score, Config, PlayerGame])
    yield db
    db.close()
