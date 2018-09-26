#!/usr/bin/env python3

##################################################
#
# track_back.py
# Steve Willson
#  9/25/18
#
##################################################

'''
track_back.py is a python script that searches elasticsearch. 
The goal is to track an ip address back to a source

Provide an IP address and time window it will initially search back from current time unless a 'current_time' is set.

track_back.py operates in 3 steps

step 1
take a destination_ip and search elasticsearch for the following fields:
return
* destination_port
* count the number of connections to that port over the time period

step 2
allow the user to select the port of interest
search elasticsearch for that destination_port and the destination_ip over the time period
return
* source_ip
* amount of data
* time connection occurred
* duration of time

step 3
allow the user to select a source_ip, this will become the next destination_ip

go to step 1 and repeat the process
build a list of the connections with the following information

source_ip: SRC_IP | dest_ip | dest_port | timestamp | session_size

'''

#Import Libraries
import argparse

import datetime

import requests

import json

#Define Argparse,
parser = argparse.ArgumentParser()

parser.add_argument('--host', action='store', dest='destination_ip_addr', help='Specify the host to search for')
parser.add_argument('-t', action='store', dest='back_time', help='Specify how back back from current_time you want to search')
parser.add_argument('-c', action='store', dest='current_time', help='Specify a current_time to start searching from')

args = parser.parse_args()

#Define character list
destination_ip_addr = args.destination_ip_addr

# change this to a time object
back_time = args.back_time

# parse the current time input, should go down to the minute
# 2018-09-25-0800
# YYYY-MM-DD-TTTT
#current_time = args.current_time

# for now, just use the current time
current_time = datetime.datetime.now()

# add an array of connections
connections = []



# if current_time is not set, use NOW

# take back_time in the form
# 2h, 2d, 2m 2h20m... etc

# pretty print arguments
def format_results(results):
    """Print results nicely:
    doc_id) content
    """
    data = [doc for doc in results['hits']['hits']]
    for doc in data:
        print("%s) %s" % (doc['_id'], doc['_source']['content']))

#split the time on days, hours, minutes

''' TODO
back_time = timedelta()

time_window = current_time - back_time
'''

# specify the elasticsearch log file to search

log_to_search = 'bro_conn'

'''
show a summary of the connections to destination_ip_addr over the time period time_window, summarize by port
'''

# STEP 1

# ELASTICSEARCH retrieve results
# DESTINATION_IP: destination_ip_addr
# TIME PERIOD: current_time - time_window

# GROUP BY: destination_port -> summarize views

uri = 'http://localhost:9200/*:logstash-*/_search'
headers = {'Content-Type': 'application/json'}
query = json.dumps({
    "size": "10000",
    "query": {
        "bool": {
            "must": [
                {"term": { "destination_ip": destination_ip_addr }}
            ],
            "filter": [
                { "range": {"@timestamp": { "gte": "now-3d/d" }}},
                { "term": {"event_type": "bro_conn" }}
            ]
        }
    }
})
response = requests.get(uri, data=query, headers=headers)
results = json.loads(response.text)

# WORKING TO THIS POINT

## summarize the destination ports

# make a table that can include all of the ports, make each dest ip a key to that dict
port_dict = {}

# make a dict that has a summary of ports

data = [doc for doc in results['hits']['hits']]
for doc in data:
    #print(doc['_source'])
    #print(doc['_source'])
    #print("The destination_port is", doc['_source']['destination_port'])
    dest_port = doc['_source']['destination_port']
    if dest_port in port_dict:
        port_dict[dest_port] += 1
    else:
        port_dict[dest_port] = 1
    #print("The destination_port is", doc['_source']['destination_port'])
    #print("The destination_ip is", doc['_source']['destination_ip'])
    #doc['_source']['destination_ip']
    #message = json.loads(doc['_source']['message'])
    #print("Time is ",message['ts'])

#print(port_dict)
print("For destination_ip: %s" % (destination_ip_addr))
for port in port_dict:
    print("Port %s was connected to %s times" % (port, str(port_dict[port])))


# summarize by dest port
    #print(doc
    #print(doc['_source'])
    #print("%s) %s" % (doc['_id'], doc['_source']['content']))
#format_results(results)

'''
allow user to choose a destination port of interest, now execute another query, this time show all SOURCE_IP addresses with timestamps and size of the session (just focused on TCP now)
'''

# STEP 2

# SELECT A PORT

port_of_interest = input('Input a port to search ')

# prompt the user to choose a port to investigate over TIME_PERIOD

# ELASTICSEARCH retrieve results
# DESTINATION_IP: destination_ip_addr
# DESTINATION_PORT: USER_CHOICE
# TIME PERIOD: current_time - time_window
# Display by: SOURCE_IP, TIME, SESSION_SIZE, SESSION_DURATION

uri = 'http://localhost:9200/*:logstash-*/_search'
headers = {'Content-Type': 'application/json'}
query = json.dumps({
    "size": "10000",
    "query": {
        "bool": {
            "must": [
                { "term": { "destination_port": int(port_of_interest) }},
                { "term": { "destination_ip": destination_ip_addr }}
            ],
            "filter": [
                { "range": {"@timestamp": { "gte": "now-3d/d" }}},
                { "term": {"event_type": "bro_conn" }},
            ]
        }
    }
})
response = requests.get(uri, data=query, headers=headers)
results = json.loads(response.text)

source_ip_dict = {}

#print(response.text)

data = [doc for doc in results['hits']['hits']]
for doc in data:
    #print(doc['_source'])
    #print(doc['_source'])
    #print("The destination_port is", doc['_source']['destination_port'])
    source_ip = doc['_source']['source_ip']
    if source_ip in source_ip_dict:
        source_ip_dict[source_ip] += 1
    else:
        source_ip_dict[source_ip] = 1
    #print("The destination_port is", doc['_source']['destination_port'])
    #print("The destination_ip is", doc['_source']['destination_ip'])
    #doc['_source']['destination_ip']
    message = json.loads(doc['_source']['message'])
    #print("Time is ",message['ts'])

#print(source_ip_dict)
print("For destination_ip %s on port %s" % (destination_ip_addr, port_of_interest))

source_ip_dict_view = [ (v,k) for k,v in source_ip_dict.items() ]
source_ip_dict_view.sort(reverse=True)
for times, source_ip in source_ip_dict_view:
    print("IP %s connected %s times" % (source_ip, times))

source_ip_addr = input('Input a source_ip address to view connections ')

'''
select the timestamp that is the most recent that has to do with the new host IP address

PROMPT allow the user to choose a specific session,
PROMPT for a new back_time
set that SOURCE_IP from the session as the DESTINATION_IP 
set the session's time to the current_time
'''

uri = 'http://localhost:9200/*:logstash-*/_search'
headers = {'Content-Type': 'application/json'}
query = json.dumps({
    "size": "10000",
    "query": {
        "bool": {
            "must": [
                { "term": { "destination_port": int(port_of_interest) }},
                { "term": { "destination_ip": destination_ip_addr }},
                { "term": { "source_ip": source_ip_addr }}
            ],
            "filter": [
                { "range": {"@timestamp": { "gte": "now-3d/d" }}},
                { "term": {"event_type": "bro_conn" }},
            ]
        }
    }
})
response = requests.get(uri, data=query, headers=headers)
results = json.loads(response.text)

timestamps = []

data = [doc for doc in results['hits']['hits']]
for doc in data:
    #print(doc['_source'])
    #print(doc['_source'])
    #print("The destination_port is", doc['_source']['destination_port'])
    #source_ip = doc['_source']['source_ip']
    #print("The destination_port is", doc['_source']['destination_port'])
    #print("The destination_ip is", doc['_source']['destination_ip'])
    #doc['_source']['destination_ip']
    message = json.loads(doc['_source']['message'])
    print("Time is ",message['ts'])
    timestamps.append(message['ts'])

timestamps.sort()

for timestamp in timestamps:
    print("Time: %s - IP %s connected to %s on port %s" % (timestamp, source_ip_addr, destination_ip_addr, port_of_interest))

timestamp = input('Input a new timestamp ')

element = {}
element['source_ip'] = source_ip_addr
element['destination_ip'] = destination_ip_addr
element['destination_port'] = port_of_interest
element['timestamp'] = timestamp

connections.append(element)

print(connections)

# source_ip | dest_ip | dest_port | timestamp | session_size

# create a new json object that has the following information
'''
APPEND THIS DATA TO THE MASTER 'track_back' list

track_back list
source_ip | dest_ip | dest_port | timestamp | session_size
source_ip | dest_ip | dest_port | timestamp | session_size
source_ip | dest_ip | dest_port | timestamp | session_size
'''

# GO BACK TO STEP 1, repeat until the user exits
