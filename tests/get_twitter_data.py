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
import logging

#from tests.test import connection_test

load_dotenv()

#Create file for Logs
logging.basicConfig(filename="get_twitter_data.log", filemode='w', format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

#Authentication with BEARER TOKEN
def auth():
    token = os.environ.get("BEARER_TOKEN")
    logger.info("Got BEARER TOKEN")
    return token

#Creates the Headers
def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    logger.info("Headers are created")
    return headers

#Creates URL for the request
def create_url(keyword, start_date, end_date, max_results = 10):
    #URL might get changed : https://developer.twitter.com/en/docs/twitter-api/early-access
    search_url = "https://api.twitter.com/2/tweets/search/all" 
    logger.info("Search URL: {url}".format(url = search_url))

    #change parameters later: https://developer.twitter.com/en/docs/twitter-api/tweets/search/api-reference/get-tweets-search-all
    query_params = {'query': keyword, 
    'start_time': start_date, 
    'end_time': end_date, 
    'max_results': max_results, 
    'expansions': 'author_id,in_reply_to_user_id,geo.place_id',
    'tweet.fields': 'id,text,author_id,in_reply_to_user_id,geo,conversation_id,created_at,lang,public_metrics,referenced_tweets,reply_settings,source',
    'user.fields': 'id,name,username,created_at,description,public_metrics,verified',
    #'place.fields': 'full_name, id, country, country_code, geo, name, place_type',
    'next_token': {}}
    logger.info("Query Params: {query}".format(query = query_params))
    return (search_url, query_params)

#Bring it all together for the request.
def connect_to_endpoint(url, headers, params, next_token = None):
    params['next_token'] = next_token #params object received from create_url function.
    response = requests.request("GET", url, headers = headers, params = params)
    print("Endpoint Respnse Code: " + str(response.status_code))

    connection_counter = 0    
    while response.status_code != 200:
        if connection_counter < 5:
            logger.error("Error message: {status_code}; {text}".format(status_code = response.status_code, text = response.text))
            print("Tries: ", connection_counter, "Sleep 30 seconds...")
            time.sleep(30)
            response = requests.request("GET", url, headers = headers, params = params)
        else:
            logger.error("Error message: {status_code}; {text}".format(status_code = response.status_code, text = response.text))
            raise Exception(response.status_code, response.text)

    #if response.status_code != 200:
    #    logger.error("Error message: {status_code}; {text}".format(status_code = response.status_code, text = response.text))
    #    raise Exception(response.status_code, response.text)
    return response.json()



#Get Start and End list
def get_star_end_list(year = 2016, month = 2, test = False):
    if test:
        runs_year = 1
        runs_month = 3
    else:
        runs_year = 5
        runs_month = 12

    for j in range(runs_year):
        for i in range(runs_month):
            start_date = "{year}-{month}-01T00:00:00.000Z".format(year = year, month = month)
            start_list.append(start_date)
            if month == 1 or month == 3 or month == 5 or month == 7 or month == 8 or month == 10 or month == 12:
                day = 31
            elif month == 4 or month == 6 or month == 9 or month == 11:
                day = 30
            elif year == 2016 or year == 2020 and month == 2:
                day = 29
            else:
                day = 28
            end_date = "{year}-{month}-{day}T00:00:00.000Z".format(year = year, month = month, day = day)
            end_list.append(end_date)
            if year == 2020 and month == 7:
                break
            elif month < 12:
                month += 1
            else:
                month = 1
                break
        year += 1
    logger.info("Start_List: {start_list} \n\tEnd_List: {end_list}".format(start_list = start_list, end_list = end_list))

def create_json(json_response):
    json_data = json_response['data']
    json_includes = json_response['includes']
    json_meta = json_response['meta']

def write_to_json(json_response):
    with open('data.json', 'w') as f:  
        json.dump(json_response, f)

#Create a custom CSV file
def create_custom_CSV():
    csvFile = open("data.csv", "a", newline="", encoding='utf-8')
    csvWriter = csv.writer(csvFile)

    #Create Headers for CSV File
    csvWriter.writerow(['author_id', 'created_at', 'tweet_id', 'lang', 'retweet_count', 'reply_count', 'like_count', 'quote_count', 'source', 'text'])
    csvFile.close()

#Enter Value to CSV File funktion
def append_to_csv(json_response, filename):
    #Counter
    counter = 0

    #Open file
    csvFile = open(filename, "a", newline="",encoding='utf-8')
    csvWriter = csv.writer(csvFile)

    #Loop through each tweet
    for tweet in json_response['data']:
        author_id = tweet['author_id']
        created_at = dateutil.parser.parse(tweet['created_at'])
        tweet_id = tweet['id']
        lang = tweet['lang']

        retweet_count = tweet['public_metrics']['retweet_count']
        reply_count = tweet['public_metrics']['reply_count']
        like_count = tweet['public_metrics']['like_count']
        quote_count = tweet['public_metrics']['quote_count']

        source = tweet['source']
        text = tweet['text'].replace('\n', '')
        
        #Combine all variables
        res = [author_id, created_at, tweet_id, lang, retweet_count, reply_count, like_count, quote_count, source, text]

        #Write res to the csv file
        csvWriter.writerow(res)
        counter += 1

    #Close the file at the end
    csvFile.close()

    #Print the number of tweets for the iteration
    print("# of Tweets added from this response: ", counter)

#Execute the request
def execute_twitter_request(total_tweets):
    for i in range(0,len(start_list)):

        #Inputs
        count = 0 #Counting number of tweets
        max_count = 10 #Max tweets per time periode
        flag = True
        next_token = None

        while flag:
            if count >= max_count:
                logger.info("Max Count is reached")
                break
            print("-----------\n {next_token}".format(next_token = next_token))
            logger.info("Next Token: {next_token}".format(next_token = next_token))
            url = create_url(keyword, start_list[i], end_list[i], max_results)
            json_response = connect_to_endpoint(url[0], headers, url[1])

            result_count = json_response['meta']['result_count']

            #Check for a new token
            if 'next_token' in json_response['meta']:
                #Save token for later
                next_token = json_response['meta']['next_token']
                print("Next Token: ", next_token)
                logger.info("Next Token: {next_token}".format(next_token = next_token))
                
                if result_count is not None and result_count > 0 and next_token is not None:
                    print("Start Date: ", start_list[i])
                    logger.info("Start with : {start_date}".format(start_date = start_list[i]))
                    write_to_json(json_response)
                    append_to_csv(json_response, "data.csv")
                    count += result_count
                    total_tweets += result_count
                    print("Total # of Tweets added: ", total_tweets)
                    logger.info("Number of tweets: {tweets}".format(tweets = total_tweets))
                    print("-------------------")
                    time.sleep(5)                
                 # If no next token exists
                else:
                    if result_count is not None and result_count > 0:
                        print("-------------------")
                        print("Start Date: ", start_list[i])
                        logger.info("Start with : {start_date}".format(start_date = start_list[i]))
                        append_to_csv(json_response, "data.csv")
                        count += result_count
                        total_tweets += result_count
                        print("Total # of Tweets added: ", total_tweets)
                        logger.info("Number of tweets: {tweets}".format(tweets = total_tweets))
                        print("-------------------")
                        time.sleep(5)
                    
                    #If this is the last request: flag to false
                    flag = False
                    next_token = None
                time.sleep(5)
    print("Total number of results: ", total_tweets)

#Funktion to run the hole script
def run_script(test = False):
    create_custom_CSV()
    get_star_end_list(test=test)
    print(start_list)
    execute_twitter_request(total_tweets)

#Inputs for the Request
bearer_token = auth()
headers = create_headers(bearer_token)
keyword = "wirecard lang:de"

start_list = []
end_list = []

max_results = 50

total_tweets = 0


#Take Action
run_script(True)

#Further To-Dos
#Write more json files to get all the information / write information into a list and write one json for each month/ hole time
#Which Keywords are important
#Do I have all required information in the CSV? 