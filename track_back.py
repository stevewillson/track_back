#!/usr/bin/env python3

##################################################
#
# track_back.py
# Steve Willson
#  9/25/18
# track_back.py is a python script that searches
# elasticsearch. Provide an IP address and time window
# it will initially search back from current time
# unless a 'current_time' is set.
#
#
##################################################

'''
It will search back from the current time unless another 'end_time'
is set. 
First, it will list by port all of the connections to this particular IP
address over the time_window

time_window = current_time - back_time

current_time can also be provided to the file

'''

#Import Libraries
import argparse

#Define Argparse,
parser = argparse.ArgumentParser()

parser.add_argument('-h', action='store', dest='host_ip_addr', help='Specify the host to search for')
parser.add_argument('-t', action='store', dest='back_time', help='Specify how back back from current_time you want to search')
parser.add_argument('-c', action='store', dest='current_time', help='Specify a current_time to start searching from')

args = parser.parse_args()

#Define character list
host_ip_addr = args.host_ip_addr

# change this to a time object
back_time = args.back_time
current_time = args.current_time

# if current_time is not set, use NOW

time_window = current_time - back_time

# specify the elasticsearch log file to search

log_to_search = 'bro_conn'

'''
show a summary of the connections to host_ip_addr over the time period time_window, summarize by port
'''

# STEP 1

# ELASTICSEARCH retrieve results
# DESTINATION_IP: host_ip_addr
# TIME PERIOD: current_time - time_window
# GROUP BY: destination_port - summarize views

'''
allow user to choose a destination port of interest, now execute another query, this time show all SOURCE_IP addresses with timestamps and size of the session (just focused on TCP now)
'''

# STEP 2

# SELECT A PORT

# prompt the user to choose a port to investigate over TIME_PERIOD

# ELASTICSEARCH retrieve results
# DESTINATION_IP: host_ip_addr
# DESTINATION_PORT: USER_CHOICE
# TIME PERIOD: current_time - time_window
# Display by: SOURCE_IP, TIME, SESSION_SIZE, SESSION_LENGTH?

'''
PROMPT allow the user to choose a specific session,
PROMPT for a new back_time
set that SOURCE_IP from the session as the DESTINATION_IP 
set the session's time to the current_time
'''

# GO BACK TO STEP 1, repeat until the user exits

