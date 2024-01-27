import json, os
import logging
import urllib

import pytest
from flask import Flask, url_for

from rest.app import create_app

log = logging.getLogger("rx")

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

""" Test Sample KPI endpoint availability """
def test_sample_kpi_endpoint(client):
    response = client.get("/sample/kpis")
    assert response.status_code == 200

""" Test Sample KPI list data """
def test_sample_kpi_list(client):
    sample_kpi_data = { "name": "Id", "index": ["H","L"], "data": [2,2] }
    response = client.get("/sample/kpis")
    assert len(response.json["data"]) == len(sample_kpi_data["data"])

""" Test Sample Data endpoint availability """
def test_sample_data_endpoint(client):
    response = client.get("/sample/")
    assert response.status_code == 200

""" Test Sample Data list count data """
def test_sample_data_default_list(client):
    sample_data_response = { "columns": [ "Id", "Location", "Time", "Description", "Severity", "Datetime" ], 
                         "index": [ 0, 1, 2, 3 ], "data": [ [ 1, "Unknown", "2020-09-15 00:21:03.234522", "Outdoor", "H", 1600129263234 ], [ 2, "A", "2020-09-15 00:21:03.527954", "Indoor", "L", 1600129263527 ], [ 3, "B", "2020-09-15 00:20:56.899683", "Roof", "H", 1600129256899 ], [ 4, "C", "2020-09-15 00:21:04.402278", "Parking", "L", 1600129264402 ] ] }
    response = client.get("/sample/")
    assert len(response.json["data"]) == len(sample_data_response["data"])

""" Test Sample Data list query data """
def test_sample_data_query_list(client):
    sample_data_response = { "columns": [ "Id", "Location", "Time", "Description", "Severity", "Datetime" ], "index": [ 0 ], "data": [ [ 4, "C", "2020-09-15 00:21:04.402278", "Parking", "L", 1600129264402 ] ] }
    data = {"location_name": "C"}
    query = urllib.parse.urlencode(data) 
    response = client.get("/sample/" + "?" + query)
    assert len(response.json["data"]) == len(sample_data_response["data"])