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

#Define Argparse,
parser = argparse.ArgumentParser()

parser.add_argument('--host', action='store', dest='host_ip_addr', help='Specify the host to search for')
parser.add_argument('-t', action='store', dest='back_time', help='Specify how back back from current_time you want to search')
parser.add_argument('-c', action='store', dest='current_time', help='Specify a current_time to start searching from')

args = parser.parse_args()

#Define character list
host_ip_addr = args.host_ip_addr

# change this to a time object
back_time = args.back_time

# parse the current time input, should go down to the minute
# 2018-09-25-0800
# YYYY-MM-DD-TTTT
#current_time = args.current_time

# for now, just use the current time
current_time = datetime.datetime.now()

# if current_time is not set, use NOW

# take back_time in the form
# 2h, 2d, 2m 2h20m... etc

#split the time on days, hours, minutes

''' TODO
back_time = timedelta()

time_window = current_time - back_time
'''

# specify the elasticsearch log file to search

log_to_search = 'bro_conn'

'''
show a summary of the connections to host_ip_addr over the time period time_window, summarize by port
'''

# STEP 1

# ELASTICSEARCH retrieve results
# DESTINATION_IP: host_ip_addr
# TIME PERIOD: current_time - time_window
# GROUP BY: destination_port -> summarize views

""" """
uri = "elasticsearch,9200"
query = json.dumps({
    "query": {
        "filtered" : {
            "query" : {
                "match_all" : {}
            },
            "filter" : {
                "destination_ip": host_ip_addr,
                "event_type": log_to_search,
                "time_period": current_time - back_time
            }
        }
    }
})
response = requests.get(uri, data=query)
results = json.loads(response.text)

'''
allow user to choose a destination port of interest, now execute another query, this time show all SOURCE_IP addresses with timestamps and size of the session (just focused on TCP now)
'''

# STEP 2

# SELECT A PORT

port_of_interest = input('Input a port to search')

# prompt the user to choose a port to investigate over TIME_PERIOD

# ELASTICSEARCH retrieve results
# DESTINATION_IP: host_ip_addr
# DESTINATION_PORT: USER_CHOICE
# TIME PERIOD: current_time - time_window
# Display by: SOURCE_IP, TIME, SESSION_SIZE, SESSION_DURATION

""" """
uri = "elasticsearch,9200"
query = json.dumps({
    "query": {
        "filtered" : {
            "query" : {
                "match_all" : {}
            },
            "filter" : {
                "destination_ip": host_ip_addr,
                "destination_port": port_of_interest,
                "event_type": log_to_search,
                "time_period": current_time - back_time
            }
        }
    }
})
response = requests.get(uri, data=query)
results = json.loads(response.text)

'''
PROMPT allow the user to choose a specific session,
PROMPT for a new back_time
set that SOURCE_IP from the session as the DESTINATION_IP 
set the session's time to the current_time
'''

session = input('Input an ip address to track')

""" """
uri = "elasticsearch,9200"
query = json.dumps({
    "query": {
        "filtered" : {
            "query" : {
                "match_all" : {}
            },
            "filter" : {
                "destination_ip" : host_ip_addr,
                "event_type": log_to_search,
                "time_period": current_time - back_time
            }
        }
    }
})
response = requests.get(uri, data=query)
results = json.loads(response.text)

'''
APPEND THIS DATA TO THE MASTER 'track_back' list

track_back list
source_ip | dest_ip | dest_port | timestamp | session_size
source_ip | dest_ip | dest_port | timestamp | session_size
source_ip | dest_ip | dest_port | timestamp | session_size
source_ip | dest_ip | dest_port | timestamp | session_size
'''


# GO BACK TO STEP 1, repeat until the user exits

