import csv
import logging
from typing import Counter

logging.basicConfig(filename="testlog.log", filemode='w', format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

logger.debug("DEBUG")
logger.info("Es ist dies und jenes passiert")
logger.info("Es ist nun etwas anderes passiert")

csvFile = open("test.csv", "a", newline="", encoding='utf-8')
csvWriter = csv.writer(csvFile, delimiter=';')

def check():
    print("check_test")

#Create Headers for CSV File
csvWriter.writerow(['Tobias', 'Helena'])
logger.info("Die Überschriften sind geschrieben")

csvFile.close()
def write_infos(filename):
    #Counter
    counter = 0

    #Open file
    csvFile = open(filename, "a", newline="",encoding='utf-8')
    csvWriter = csv.writer(csvFile, delimiter = ';')
    logger.info("Wir gehen in die FOR schleife")
    for i in range(10): 

        a = "a", i
        b = "b", i

        res = [a, b]
        
        csvWriter.writerow(res)
        counter += 1
        print(i)
        logger.info("Schleife: {num}".format(num = i))
logger.info("ausführen der Funktion")
write_infos("test.csv")

logger.info("ENDE")
#csvWriter.writerow(['Helena', 'Tobias'])

status_code = 201
def connection_test():
    status_code = 198
    while status_code != 200:
        print("FALSE", status_code)
        status_code += 1
    print("Works Status code = ", status_code)

connection_test()
print("TEST!123")  

#year = 2016
#month = 2
start_list = []
end_list = []
def get_start_end(year = 2016, month = 2):
    num_of_runs = 0
    for j in range(5):
        for i in range(12):
            start_date = "{year}-{month}-01T00:00:00.000Z".format(year = year, month = month)
            start_list.append(start_date)
            num_of_runs += 1
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
            print("Start: ",start_date)
            print("End: ",end_date)
            print("")
            if year == 2020 and month == 7:
                break
            elif month < 12:
                month += 1
            else:
                month = 1
                break
        year += 1
    print("Durchläufe", num_of_runs)
get_start_end()

print(start_list)
print(end_list)

#print(start_list[8])
#print(end_list[8])

def ausgabe(jahr = 2020, monat = 1, test = False):
    if test:
        print(jahr)
        print(monat)
        print(test_variable_nach_fkt)
    else:
        print("Kotstulle")

test_variable_nach_fkt = "Das ist ein Test"
ausgabe(test=True)

import json

filename = 'your_file.json'
lst = {'data':[{'alice': 24}, {'bob': 27}],'meta':[{'name':2}, {'age':2}]}

# Write the initial json object (list of dicts)
with open(filename, mode='w') as f:
    json.dump(lst, f)

print(lst['data'])

# Append the new dict to the list and overwrite whole file
def add_to_json():
    more = {'carl':33}
    with open(filename, mode='w') as f:
        #lst.append({'data':{'carl':33}})
        lst['data'].append(more)
        json.dump(lst, f)

add_to_json()