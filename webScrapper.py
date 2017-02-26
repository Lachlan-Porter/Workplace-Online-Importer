import requests
import os
import datetime
from bs4 import BeautifulSoup
from OAuth_cal import loadCustomEvent

def main():
    print("Updating calendar with any new shifts")
    #store the details we need to login to workplace online
	#removed for privacy reasons
    payload = {
        "account" : "...",
        "username": "...",
        "password": "...",
        "task": "Sign In"
    }

    #https://www.quora.com/What-is-the-best-way-to-log-in-to-a-website-using-Python
    # -- Kashyap Raval reply, Aug 6 (accessed 20/1/2017)
    #This logs into page using data set up above using sesson and post
    with requests.Session() as s:
        p = s.post('https://champions.workplaceonline.com.au/c2/signin/', data=payload)
        #use beautiful soup to find the relevant shift times
        soup = BeautifulSoup(p.text, "html.parser")
    
    #find all the text in the page
    text = soup.text
    
    #split the page into sections 
    #NOTE: did this through string manipulation as bs4 was being weird and only returning two table rows
    #EG everything after My Shifts but before Calendar
    sections = text.split('My Shifts')
    shifts = sections[1].split('Calendar')[0]

    #divide shift information into lines
    lines = shifts.split('\n')

    #set up a dictionary to create the events with 
    times = parseShiftStringToDateTime(lines)

    loadCustomEvent(times)

def parseShiftStringToDateTime(lines):
    "Turns the string lines into a dictionary startTime : endTime"
    #input is in the form of:
    #
    #Tomorrow           <-- date line
    #2:00PM-8:00PM      <-- time line
    #26/02
    #5:00PM-8:00PM
    #
    #this will return a dictionary like (date of writing is 24/02/2017):
    #{
    #   2017-02-25T14:00 : 2017-02-25T20:00
    #   2017-02-26T17:00 : 2017-02-26T20:00 
    #}

    #BAD REPLACE SOON
    CURRENT_YEAR = '2017'

    shiftData = {}
    shiftDate = 'placeHolder'
    shiftTimes = None
    for line in lines:
        #if the line is not whiteSpace (no data)
        if line.strip():
            #find out if this is a date or time line
            shiftTimes = line.split('-')
            if(len(shiftTimes) == 1):
                #must be date line since no '-' present
                if(line == 'Tomorrow'):
                    #calculate tomorrow's date by adding one day to today 
                    line = datetime.date.today() + datetime.timedelta(days=1)
                    line = str(line)
                elif(line == 'Today'):
                    line = datetime.date.today()
                    line = str(line)
                else: #26/02 into 2017-02-26
                    #format string in the correct form
                    line = CURRENT_YEAR + '-' + line
                    line = line.replace('/', '-')
                    line = dateFormat(line)
                #store this date for use on the next loop (time line)
                shiftDate = line
            else:
                #must be time line
                start = shiftDate + ' ' + shiftTimes[0]
                end = shiftDate + ' ' + shiftTimes[1]
                start =datetime.datetime.strptime(start, "%Y-%m-%d %I:%M%p")
                start = start.isoformat()
                end = datetime.datetime.strptime(end, "%Y-%m-%d %I:%M%p")
                end = end.isoformat()
                shiftData.update({start : end})
    return shiftData

def dateFormat(string):
    "formats a date from (year/day/month) to (year/month/day) assuming perfect input"
    #for use to turn 
    #2017-26-02 (year/day/month)
    #into
    #2017-02-26 (year/month/day) <-- standard format
    #
    #kinda hackery but its just for me so meh
    #WARNING: ASSUMES PERFECT INPUT IN FORM ABOVE
    temp1 = string[5]
    temp2 = string[6]

    stringl = list(string)

    stringl[5] = string[8]
    stringl[6] = string[9]

    stringl[8] = temp1
    stringl[9] = temp2

    return ''.join(stringl)

if __name__ == '__main__':
    main()

#keep console open after script has been run
os.system("pause")