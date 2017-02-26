#Learning how to use OAuth2 and google calendar api

#GOAL: To be able to create an event with a specific time
#      so that I can use this for the larger importer project

#These libraies are the ones used in the quickstart python example
#Most of this code will be based/copied from that file
#In order to learn how to use OAuth 2.0 we must first understand the quickstart code


from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import datetime


try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None
#convention copied from quickstart
#define constants for later use (makes more readable)
SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Importer'

#DIRECTLY COPIED FROM quickstart.py
#broken down line by line with comments for understanding
def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    #
    #	Most of the first half is pathing stuff 
    #	This information on this can be found at the link below
    #	https://docs.python.org/2/library/os.path.html
    #

    #expanduser finds the users home directory 
    #in this case, C:\Users\Lachlan
    home_dir = os.path.expanduser('~')
    #if there is a folder called '.credentials' store a new directory path
    credential_dir = os.path.join(home_dir, '.credentials')
    #if it cannot find this directory create it
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    #create or join a path to a file with credential info
    credential_path = os.path.join(credential_dir,
                                   'Importer.json')

    #
    #	This is where the OAuth 2.0 stuff comes into play
    #	https://developers.google.com/api-client-library/python/guide/aaa_oauth
    #

    #stores the crendials in OAuth storage object
    store = Storage(credential_path)
    #retreives the credentials for use in creating flow
    credentials = store.get()
    #if the credentials doesnt exist or is invalid, try to validate it with
    #client secret file along with app name constant declared above
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def main():
    """Shows basic usage of the Google Calendar API.

    """
    #find credentials 
    credentials = get_credentials()
    #Authorises credentials, more info here -
    #http://oauth2client.readthedocs.io/en/latest/source/oauth2client.client.html#oauth2client.client.Credentials.authorize 
    http = credentials.authorize(httplib2.Http())
    #create a resource to interact with google api
    #in this case the calendar api, version 3 using the httplib2 declared above
    service = discovery.build('calendar', 'v3', http=http)
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print(now)
    event = {
    	'summary': 'TEST EVENT PLS IGNORE',
    	'start': {
    		'dateTime' : '2017-02-25T05:30:00',
    		'timeZone' : 'Australia/Victoria',
    	},
    	'end': {
    		'dateTime' : '2017-02-25T06:30:00',
    		'timeZone' : "Australia/Victoria",
    	},
    }
    event = service.events().insert(calendarId='primary', body=event).execute()
    print('Event created: %s' % (event.get('htmlLink')))

def loadCustomEvent(times):
	#find credentials 
    credentials = get_credentials()
    #Authorises credentials
    http = credentials.authorize(httplib2.Http())
    #create a resource to interact with google api
    #in this case the calendar api, version 3 using the httplib2 declared above
    service = discovery.build('calendar', 'v3', http=http)

    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    #get the next 100 events (to avoid making duplicates)
    eventsResult = service.events().list(
        calendarId='primary', timeMin=now, maxResults=100, singleEvents=True,
        orderBy='startTime').execute()
    events = eventsResult.get('items', [])

    for key in times:
	    shift = {
	    	'summary': 'Work',
	    	'start': {
	    		'dateTime' : key,
	    		'timeZone' : 'Australia/Victoria',
	    	},
	    	'end': {
	    		'dateTime' : times[key],
	    		'timeZone' : "Australia/Victoria",
	    	},
	    	'description' : 'Auto generated by Lachlan Porters webscrapper python script',
	    }
	    duplicateEvent = False
	    for event in events:
	    	if(event['start'].get('dateTime') == key + "+11:00"):
	    		duplicateEvent = True
	    if not duplicateEvent:
	    	shift = service.events().insert(calendarId='primary', body=shift).execute()
	    	print("Inserted new event")
	    else:
	    	print("Found duplicate shift on " + key)


if __name__ == '__main__':
    main()