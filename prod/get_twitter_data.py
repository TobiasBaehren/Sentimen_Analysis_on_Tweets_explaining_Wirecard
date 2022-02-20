from cgi import test
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
    logger.info("Start with create_url()")

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
    logger.info("Start with connect_to_endpoint()")

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
            connection_counter += 1
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
        year = 2020
        month = 4
        runs_year = 1
        runs_month = 2
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
#Create initial Json File structure
json_file = {'data':[], 'includes':{'users':[], 'places':[]}, 'meta':{'newest_id':[], 'oldest_id':[], 'result_count':[], 'next_token':[]}}
current_year = 0


#Writes information to JSON File
def write_to_json(json_response, start):
    global current_year
    global keyword

    #Checks if I have to start a new JSON file
    #JSON file for each year. 
    if current_year != start[0:4]:
        global json_file
        json_file = {'data':[], 'includes':{'users':[], 'places':[]}, 'meta':{'newest_id':[], 'oldest_id':[], 'result_count':[], 'next_token':[]}}
        current_year = start[0:4]
        print(current_year)
    #json_filename = "{year}_{keyword}_data.json".format(year = start[0:4], keyword = keyword.split()[0])
    json_filename = "{year}_data.json".format(year = start[0:4])

    #Opens the JSON file to write
    with open(json_filename, mode = 'w') as f:
        #Checks for the required information inth response and writes the data to the JSON file 
        if 'data' in json_response:
            for each_data in range(0,len(json_response['data'])):
                json_file['data'].append(json_response['data'][each_data])

        if 'includes' in json_response:
            if 'users' in json_response['includes']:
                for each_users in range(0,len(json_response['includes']['users'])):
                    json_file['includes']['users'].append(json_response['includes']['users'][each_users])

            if 'places' in json_response['includes']:
                for each_places in range(0,len(json_response['includes']['places'])):
                    json_file['includes']['places'].append(json_response['includes']['places'][each_places])

        if 'meta' in json_response:
            if 'newest_id' in json_response['meta']:
                json_file['meta']['newest_id'].append(json_response['meta']['newest_id'])
            if 'oldest_id' in json_response['meta']:    
                json_file['meta']['oldest_id'].append(json_response['meta']['oldest_id'])
            if 'result_count' in json_response['meta']:
                json_file['meta']['result_count'].append(json_response['meta']['result_count'])
            if 'next_token' in json_response['meta']:
                json_file['meta']['next_token'].append(json_response['meta']['next_token'])

        #Save the data to the JSON file
        json.dump(json_file, f)

# def write_to_json(json_response,start):
#     with open('data.json', 'w') as f:  
#         json.dump(json_response, f)

#Create a custom CSV file
def create_custom_CSV():
    csvFile = open("data.csv", "a", newline="", encoding='utf-8')
    csvWriter = csv.writer(csvFile, delimiter=';')

    #Create Headers for CSV File
    csvWriter.writerow(['conversation_id','author_id', 'created_at', 'tweet_id', 'lang', 'retweet_count', 'reply_count', 'like_count', 'quote_count', 'source', 'tweet_type', 'referenced_tweet_id', 'text'])
    csvFile.close()

    csvFile_user = open("user.csv", "a", newline="", encoding='utf-8')
    csvWriter_user = csv.writer(csvFile_user, delimiter=';')

    #Create Headers for CSV File
    csvWriter_user.writerow(['user_id', 'username', 'name', 'follower', 'following', 'tweet_cound', 'list_count', 'verified', 'created_at'])
    csvFile_user.close()

#Enter Value to CSV File funktion
def append_to_csv(json_response, filename):
    logger.info("append_to_csv is started wiht file {file}".format(file = filename))
    
    #Counter
    counter = 0

    #Open file
    csvFile = open(filename, "a", newline="",encoding='utf-8')
    csvWriter = csv.writer(csvFile, delimiter=';')

    #Loop through each tweet
    if filename == "data.csv":
        for tweet in json_response['data']:
            conversation_id = tweet['conversation_id']
            author_id = tweet['author_id']
            created_at = dateutil.parser.parse(tweet['created_at'])
            tweet_id = tweet['id']
            lang = tweet['lang']

            retweet_count = tweet['public_metrics']['retweet_count']
            reply_count = tweet['public_metrics']['reply_count']
            like_count = tweet['public_metrics']['like_count']
            quote_count = tweet['public_metrics']['quote_count']

            source = tweet['source']
            
            tweet_type = []
            referenced_tweet_id = []
            if 'referenced_tweets' in tweet:
                for each in range(0,len(tweet['referenced_tweets'])):
                    tweet_type.append(tweet['referenced_tweets'][each]['type'])
                    referenced_tweet_id.append(tweet['referenced_tweets'][each]['id'])
            else:
                tweet_type.append(None)
                referenced_tweet_id.append(None)

            text = tweet['text'].replace('\n', '')
            
            #Combine all variables
            res = [conversation_id, author_id, created_at, tweet_id, lang, retweet_count, reply_count, like_count, quote_count, source, tweet_type, referenced_tweet_id, text]

            #Write res to the csv file
            csvWriter.writerow(res)
            counter += 1
            #Close the file at the end
        csvFile.close()

        #Print the number of tweets for the iteration
        print("# of Tweets added from this response: ", counter)

    elif filename == "user.csv" and json_response['includes']['users']: 

        for user in json_response['includes']['users']:
            user_id = user['id']
            username = user['username']
            name = user['name']

            follower = user['public_metrics']['followers_count']
            following = user['public_metrics']['following_count']
            tweet_count = user['public_metrics']['tweet_count']
            list_count = user['public_metrics']['listed_count']

            verified = user['verified']
            user_created_at = dateutil.parser.parse(user['created_at'])

            #Combine all variables
            res = [user_id, username, name, follower, following, tweet_count, list_count, verified, user_created_at]

            #Write res to the csv file
            csvWriter.writerow(res)
            counter += 1
        #close the file at the end
        csvFile.close()

        #Print the number of users of the interation
        print("# of Users added from this response: ", counter)



#Execute the request
def execute_twitter_request(total_tweets):
    logger.info("For Loop starts for {length} runs.".format(length = len(start_list)))
    for i in range(0,len(start_list)):
        logger.info("For Loop run: {runs}".format(runs = i))

        #Creat JSON File Name
        #json_filename = start_list[i],'_data.json'

        #Inputs
        count = 0 #Counting number of tweets
        max_count = 90000 #Max tweets per time periode
        flag = True
        next_token = None

        while flag:
            logger.info("Start with WHILE loop.")

            if count >= max_count:
                logger.info("Max Count is reached")
                break
            print("-----------\n {next_token}".format(next_token = next_token))
            logger.info("Start Token: {next_token}".format(next_token = next_token))
            url = create_url(keyword, start_list[i], end_list[i], max_results)
            json_response = connect_to_endpoint(url[0], headers, url[1], next_token)

            result_count = json_response['meta']['result_count']

            #Check for a new token
            if 'next_token' in json_response['meta']:
                #Save token for later
                logger.info("if condition: next_token is in json_response")
                next_token = json_response['meta']['next_token']
                print("Next Token: ", next_token)
                logger.info("Next Token: {next_token}".format(next_token = next_token))
                
                if result_count is not None and result_count > 0 and next_token is not None:
                    logger.info("if condition: result_count is not None and result_count > 0 and next_token is not None")
                    print("Start Date: ", start_list[i])
                    logger.info("-------------------")
                    logger.info("Start with : {start_date}".format(start_date = start_list[i]))
                    write_to_json(json_response, start_list[i])
                    append_to_csv(json_response, "data.csv")
                    append_to_csv(json_response, "user.csv")
                    count += result_count
                    total_tweets += result_count
                    print("Total # of Tweets added: ", total_tweets)
                    logger.info("Number of tweets: {tweets}".format(tweets = total_tweets))
                    logger.info("-------------------")
                    print("-------------------")
                    time.sleep(5)                
             # If no next token exists
            else:
                logger.info("else condition: next_token is in json_response")
                if result_count is not None and result_count > 0:
                    logger.info("result_count is not None and result_count > 0")
                    print("-------------------")
                    print("Start Date: ", start_list[i])
                    logger.info("-------------------")
                    logger.info("Start with : {start_date}".format(start_date = start_list[i]))
                    append_to_csv(json_response, "data.csv")
                    append_to_csv(json_response, "user.csv")                    
                    write_to_json(json_response, start_list[i])
                    count += result_count
                    total_tweets += result_count
                    print("Total # of Tweets added: ", total_tweets)
                    logger.info("Number of tweets: {tweets}".format(tweets = total_tweets))
                    logger.info("-------------------")
                    print("-------------------")
                    time.sleep(5)
                    
                #If this is the last request: flag to false
                logger.info("Set flag to False and next_token to None")
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
keyword = '(MarkusBraun OR "Markus Braun" OR JanMarsalek OR "Jan Marsalek") lang:en'

#The following keyword query is not used because all further keywords are implemented in the first search for wirecard.
#No further informtaion will be genereated. Furhtermore, I cannot look for just a keyword like "BaFin" because they handle to many different tasks, like Bitcoin in 2018.

# keyword = ('((MarkusBraun OR "Markus Braun" OR JanMarsalek OR "Jan Marsalek") OR '
# '((EY OR "Ernst&Young" OR "Ernst & Young" OR '
# 'BAFIN OR BundesanstaltfürFinanzdienstleistungsaufsicht OR BundesanstaltfuerFinanzdienstleistungsaufsicht OR "Bundesanstalt für Finanzdienstleistungsaufsicht" OR "Bundesanstalt fuer Finanzdienstleistungsaufsicht" OR '
# 'FIU OR "Zentralstelle für Finanztransaktionsuntersuchungen" OR "Zentralstelle fuer Finanztransaktionsuntersuchungen" OR ZentralstellefürFinanztransaktionsuntersuchungen OR ZentralstellefuerFinanztransaktionsuntersuchungen OR '
# 'DPR OR DeutschePrüfstellefürRechnungslegung OR DeutschePruefstellefuerRechnungslegung OR "Deutsche Prüfstelle für Rechnungslegung" OR "Deutsche Pruefstelle fuer Rechnungslegung" OR '
# 'APAS OR Abschlussprüferaufsichtskommission OR Abschlussprueferaufsichtskommission OR AuditorOversightCommission OR "Auditor Oversight Commission" OR'
# 'KPMG) '
# 'Wirecard)) lang:de')

start_list = []
end_list = []

max_results = 500

total_tweets = 0


#Take Action
#run_script(True)
run_script()

# Further To-Dos
# Which Keywords are important

#Keywords I have used: 
#   wirecard lang:de
#   wirecard lang:en
#   (MarkusBraun OR "Markus Braun" OR JanMarsalek OR "Jan Marsalek") lang:de