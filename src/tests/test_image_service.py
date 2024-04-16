import json, os
import logging
import urllib

import pytest
from flask import Flask, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

from rest.app import create_app

log = logging.getLogger("rx")

# -------------------------- #
# Initialize Database Model  #
# -------------------------- #
class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
    })
    yield app

@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture()
def runner(app):
    return app.test_cli_runner()

""" Test Images endpoint availability """
def test_images_endpoint(client):
    response = client.get("/images")
    assert response.status_code == 200

""" Test Images count """
def test_images_count(client):
    images_data_len = 3
    response = client.get("/images")
    assert len(response.json["data"]) == 3

