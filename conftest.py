import pytest

import example.app


@pytest.fixture
def app():
    return example.app.app


@pytest.fixture
def db():
    return example.app.connect_db()
