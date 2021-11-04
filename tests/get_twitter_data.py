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

def create_url(keyword, start_date, end_date, max_results = 10):
    #URL might get changed : https://developer.twitter.com/en/docs/twitter-api/early-access
    search_url = "https://api.twitter.com/2/tweets/search/all" 

    #change parameters later: https://developer.twitter.com/en/docs/twitter-api/tweets/search/api-reference/get-tweets-search-all
    query_params = {'query': keyword, 
    'start_time': start_date, 
    'end_time': end_date, 
    'max_results': max_results, 
    #'expansions': 'author_id, in_reply_to_user_id, geo.place_id',
    #'tweet.fields': 'id, text, author_id, in_reply_to_user_id, geo, conversation_id, created_at, lang, public_metrics, referenced_tweets, reply_settings, source',
    #'user.fields': 'id, name, username, created_at, description, public_metrics, verified',
    #'place.fields': 'full_name, id, country, country_code, geo, name, place_type',
    'next_token': {}}

    return (search_url, query_params)

def connect_to_endpoint(url, headers, params, next_token = None):
    params['next_token'] = next_token #params object received from create_url function.
    response = requests.request("GET", url, headers = headers, params = params)
    print("Endpoint Respnse Code: " + str(response.status_code))
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()

#Inputs for the Request
bearer_token = auth()
headers = create_headers(bearer_token)
keyword = "wirecard lang:de"
start_time = "2020-01-01T00:00:00.000Z"
end_time = "2020-12-31T00:00:00.000Z"
max_results = 10

url = create_url(keyword, start_time, end_time, max_results)
json_response = connect_to_endpoint(url[0], headers, url[1])

print(json.dumps(json_response, indent=4, sort_keys=True))

#json_response['data'][0]['create_at']
#json_response['meta']['result_count']

with open('data.json', 'w') as f:  
    json.dump(json_response, f)