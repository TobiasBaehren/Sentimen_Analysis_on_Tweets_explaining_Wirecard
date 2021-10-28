import requests
import os
import json
import pandas as pd
import csv
import datetime
import dateutil.parser
import unicodedata
import time
from dotenv import load_dotenv

load_dotenv()

def auth():
    token = os.environ.get("BEARER_TOKEN")
    return token

def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers

#def create_url(keyword, start_date, end_date, max_results = 10):
