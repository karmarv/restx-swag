import json, os
import logging
import sys, time
import datetime
import pandas as pd

from flask import Flask, Response, jsonify, make_response
from flask_restx import Namespace, Resource, fields
from flask_restx import reqparse
from flask.logging import default_handler

from rest.services import config
from rest.services.data.sample_dao import init_sample_data
from rest.services.data.database import setup_db

log = logging.getLogger("rx")
api = Namespace('sample', description='Operations related to Sample data')

#
# Initialize the In-memory Datastore
#
datastore_sample_df = init_sample_data()


""" Filter by time """
def filter_time(data, query_time):
    if "-" in query_time:
        hrs = query_time.split("-")
        start, end = datetime.time(int(hrs[0]), 0, 0), datetime.time(int(hrs[1]), 0, 0)
        # start = pd.Timestamp(year=int(query_date_str[0]), month=int(query_date_str[1]), day=int(query_date_str[2]), hour=int(hrs[0]))
        # end   = pd.Timestamp(year=int(query_date_str[0]), month=int(query_date_str[1]), day=int(query_date_str[2]), hour=int(hrs[1]))  
        filtered_data = data.between_time(start, end)
    else:
        hr = datetime.time(int(query_time), 0, 0)
        filtered_data = data.loc[(data['Datetime'] == hr)]
    return filtered_data

#
# Service functions
#
def fetch_samples(location_name, query_time = None, offset=0, limit=25):
    # 1. Filter by location_name 
    if location_name is not None:
        filtered_df = datastore_sample_df[datastore_sample_df["Location"].str.contains(location_name.strip(), na=False)]
    else: 
        filtered_df = datastore_sample_df
    
    # 2. Filter by query_time
    if query_time is not None:
        filtered_df = filter_time(filtered_df, query_time)

    # 3. Limit to a records subset
    if len(filtered_df.index) > 1 and limit > 0:
        filtered_df = filtered_df[offset:limit]
    
    log.debug("Queried: {}, Count {}".format(query_time, len(filtered_df.index)))
    return filtered_df.reset_index(drop=True) 


""" Service functions """
def fetch_kpis():
    aggregate_data = datastore_sample_df.groupby(['Severity'])['Id'].count()
    return aggregate_data

# -------------------------------------- #
# Parsers: Upload, Filter and Pagination #
# -------------------------------------- #
reqp = reqparse.RequestParser()
reqp.add_argument('location_name', type=str, default=None,   required=False, help='Location name')
reqp.add_argument('query_time',    type=str, default="0-10", required=False, help='(0 or 0-10) Query time/range in day hours.')
reqp.add_argument('offset',        type=int, default=0,      required=False, help="(0) Starting index of the response")
reqp.add_argument('limit' ,        type=int, default=100,    required=False, help="Maximum size of the response. limit=0 for querying all dataset")

@api.route('/')
@api.response(404, 'Sample Data function not found.')
class DataList(Resource):
    @api.doc('get_data')
    @api.expect(reqp)
    def get(self):
        """Returns list of sample data point as indicators."""
        args = reqp.parse_args()
        data = fetch_samples(location_name=args.get('location_name'),
                            #query_date=args.get('query_date'),
                            query_time=args.get('query_time'),
                            offset=args.get('offset'),
                            limit=args.get('limit'))
        response = make_response(data.to_json(orient='split'))
        response.mimetype = 'application/json'
        return response

@api.route('/kpis')
class KpiList(Resource):
    @api.doc('get_kpi')
    def get(self):
        """Returns list of KPI data sample grouped by 'Severity' column."""
        try:
            data = fetch_kpis()
            response = make_response(data.to_json(orient='split'))
            response.mimetype = 'application/json'
            return response
        except KeyError as e:
            api.abort(500, e.__doc__, status = "Could not retrieve information", statusCode = "500")
        except Exception as e:
            api.abort(400, e.__doc__, status = "Could not retrieve information", statusCode = "400")

@api.route('/db')
class DbList(Resource):
    @api.doc('get_db')
    def get(self):
        """Configure database."""
        try:
            data = setup_db()
            response = make_response(data.to_json(orient='split'))
            response.mimetype = 'application/json'
            return response
        except KeyError as e:
            api.abort(500, e.__doc__, status = "Could not retrieve information", statusCode = "500")
        except Exception as e:
            api.abort(400, e.__doc__, status = "Could not retrieve information", statusCode = "400")