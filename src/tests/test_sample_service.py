import json, os
import logging
import tempfile

import pytest
from flask import Flask, url_for

from rest import create_app

log = logging.getLogger("rx")

@pytest.fixture
def app():
    app = create_app()
    return app

""" Test Sample Data list Service """
def test_sample_data_list(client):
    response = client.get(url_for('sample_data_list'))
    print(response)
    assert response.status_code == 200
