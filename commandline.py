import config
from feedobject import FeedObject
import os
from datetime import datetime

import sys

"""
TODO - seperate the two addplayers options into two main menu options
TODO - ways to delete players
TODO - regex analysis method
TODO - exportation methods to spreadsheet
TODO - database last updated

"""
import httplib2

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Sheets API Python Quickstart'

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def clear():
    os.system('cls')


def checkusername(name):
    if len(name)<1 or len(name)>12:
        return False
    if(name[0] in " -_" or name[-1] in " -_"):
        return False
    for c in name:
        if not (c.lower() in "abcdefghijklmnopqrstuvwxyz1234567890 -_"):
            return False

    return True
def UpdateCurrentEvents():
    f = open(config.updatelog,"a")
    f.write("=== Update on {0} ===\n".format(datetime.utcnow().strftime(config.timestring)))
    try:
        new_items = 0

        nofeedplayers = []

        result = config.feeds.update()
        print("=== Results ===")
        if(len(result)==0):
            print("(None)")
        else:
            new_entries = 0

            for item in result: # loop through the big list of messages
                new_entries += item.new_entries

                for msg in item.warning_messages:
                    print("[{0}]: {1}".format(item.username,msg))

                    if(msg.startswith("Did not get feeds ")): # assume only one such message is reported per player
                        nofeedplayers.append(item.username)
                        continue


                    f.write("[{0}]: {1}".format(item.username,msg)+"\n")


                new_items += item.new_entries

                if(item.new_entries>0):
                    f.write("{0}: {1} new items found".format(item.username,item.new_entries)+"\n")
                    print("[{0}]: {1} new items found".format(item.username,
                                                              item.new_entries))  # print number of new items found for this player
            if(new_items==0):
                f.write("(No new items)\n")
                print("(No new items)\n")
            if(len(nofeedplayers)>0):
                f.write("\nDid not get logs for the following players: " + ", ".join(nofeedplayers)+"\n")
                print("\nDid not get logs for the following players: " + ", ".join(nofeedplayers)+"\n")

    except Exception as ex:
        f.write("Error: {0}".format(ex))

    f.write("\n")
    f.close()

def SaveFeeds():
    curdir = config.default_feed_dir
    config.feeds.save_feed(curdir)
    print("Feeds saved. \n")

def InitRegex():
    if(os.path.isdir(config.regexfile)):
        print("Your regex file is a directory! Get rid of it.")
        return
    elif(not os.path.isfile(config.regexfile)):
        open(config.regexfile,"w+").close()

    f = open(config.regexfile, "r")
    lines = f.readlines()
    for i in range(0, len(lines), 2):
        line = lines[i].rstrip()
        line2 = lines[i + 1].rstrip()
        if (len(line) == 0):
            continue
        config.regex_array.append([line, line2])

def InitFeeds():
    try:
        if (config.feeds is None):
            config.feeds = FeedObject.init_feed()
    except Exception as ex:
        print("Error while attempting to create feed: {0}".format(ex))
        raise


InitRegex()


def print_help():
    print("Dr Chao Commandline Utility")
    print("Usage: ")
    print("       commandline.py update [playerfile]")
    print("       commandline.py analyze regexnumber [start-date] [end-date] [playerfile] [sheet-id] [topleft-cell] [skipzero] ")
    print("       commandline.py analyze-first [regexes] [start-date] [end-date] [player-file] [sheet-id] [topleft-cell] [none-string]")
    print("       commandline.py regexes")
    print("")
    print("Note that dates are used in YYYY-MM-DD@hh:mm format, with 24 hours. Specify 'none' for no date bounds. ")
    print("Also, the [playerfile] is relative to the directory that the script is located in. ")
    print("If the last argument is 'skipzero', then any matches with value of 0 are not added to the sheet.")
    print("")
    print("analyze-first will display the first occurrence of the regex numbers provivded.")
    print("Seperate the regex numbers with commas, i.e: '4,5' or '6,7,8'.")
    print("")
    print("A note about timestamps: The Adventurer log seems to use BST as the timezone, rather than UTC.")
    print("The time is stored as read from the server, but when comparing, the program will not make any adjustments.")
    print("It will assume that the timestamp of the event is in UTC. Please take this into consideration when setting date bounds.")
if(len(sys.argv)<=1):
    print_help()

elif(sys.argv[1].lower()=="update"):
    if(len(sys.argv)>=3):
        config.playerfile = os.path.join("..", sys.argv[2])
    InitFeeds()
    UpdateCurrentEvents()
    SaveFeeds()

elif(sys.argv[1].lower()=="analyze"):
    picks = int(sys.argv[2])

    start_date = None
    end_date = None
    sheet_id = None

    startingCell = 'A1'

    skipZero = False
    sort = False

    if(len(sys.argv)>= 4):
        start_date = datetime.strptime(sys.argv[3],"%Y-%m-%d@%H:%M") if sys.argv[3].lower() != "none" else None
    if(len(sys.argv)>=5):
        end_date = datetime.strptime(sys.argv[4],"%Y-%m-%d@%H:%M")  if sys.argv[4].lower() != "none" else None
    if(len(sys.argv)>=6):
        config.playerfile = os.path.join("..",sys.argv[5]) #so when feedsobject loads this, it searches in the parent directory huh
    if(len(sys.argv)>=7):
        sheet_id = sys.argv[6]
    if(len(sys.argv)>=8):
        startingCell = sys.argv[7]
    #rest of the arguments
    for i in range(8, len(sys.argv)):
        if(sys.argv[i] == "skipzero"):
            skipZero = True
        elif(sys.argv[i] == "sort"):
            sort = True
    InitFeeds()


    picked_regexes = config.regex_array[picks - 1]
    #TODO: error checking n shit
    if (start_date is not None):
        print("Picked start date", start_date.strftime(config.timestring))
    if (end_date is not None):
        print("Picked end", end_date.strftime(config.timestring))

    result = config.feeds.count_matches(picked_regexes[1], start_date, end_date, skipZero)
    print("\n=== " + picked_regexes[0] + " ===")
    if (start_date is not None):
        print("Starting at", start_date.strftime(config.timestring))
    if (end_date is not None):
        print("Ending at", end_date.strftime(config.timestring))
        print("")

    if(sort):
        # the default count first order
        # -x[1] : the points in reverse order, as primary key.
        # x[0].username : the username as the secondary key.
        result = sorted(result, key = lambda x: (-x[1], x[0].username))

    for i in range(0,len(result)):
        item = result[i]

        print(item[0].username + ": " + str(item[1]))

        result[i][0] = result[i][0].username #yah cuz i can do dis in python. sick typing.


    if(sheet_id is not None):
        credentials = get_credentials()
        http = credentials.authorize(httplib2.Http())
        discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                        'version=v4')
        service = discovery.build('sheets', 'v4', http=http,
                                  discoveryServiceUrl=discoveryUrl)

        spreadsheetId = sheet_id

        values = [
            [
                "Player",picked_regexes[0]
                #,
                #"Starting at " + start_date.strftime(config.jsontimestring) if start_date is not None else "",
                #"Ending at " + end_date.strftime(config.jsontimestring) if end_date is not None else ""
            ]

        ] + result

        data = [
            {
                'range': startingCell,
                'values': values
            }
            # Additional ranges to update ...
        ]
        body = {
            'valueInputOption': "raw",
            'data': data
        }

        result = service.spreadsheets().values().batchUpdate(
            spreadsheetId=spreadsheetId, body=body).execute()

        print("Total updated cells in spreadsheet: {0}".format(result["totalUpdatedCells"]))
elif(sys.argv[1].lower()=="analyze-first"):
    #####

    ###### ANALYZE - FIRST

    picks = [int(x.strip()) for x in sys.argv[2].split(',')]

    start_date = None
    end_date = None
    sheet_id = None

    startingCell = 'A1'

    timestring = config.jsontimestring
    nonestring = "None";

    if(len(sys.argv)>= 4):
        start_date = datetime.strptime(sys.argv[3],"%Y-%m-%d@%H:%M") if sys.argv[3].lower() != "none" else None
    if(len(sys.argv)>=5):
        end_date = datetime.strptime(sys.argv[4],"%Y-%m-%d@%H:%M")  if sys.argv[4].lower() != "none" else None
    if(len(sys.argv)>=6):
        config.playerfile = os.path.join("..",sys.argv[5]) #so when feedsobject loads this, it searches in the parent directory huh
    if(len(sys.argv)>=7):
        sheet_id = sys.argv[6]
    if(len(sys.argv)>=8):
        startingCell = sys.argv[7]
    if (len(sys.argv) >= 9):
        nonestring= sys.argv[8]

    InitFeeds()


    picked_regexes = [config.regex_array[x-1] for x in picks]

    # not really sure how efficient this is. probably not very. but hey, python syntax is pretty damn amazing.
    regexnames = [i[0] for i in picked_regexes]
    regexpatterns = [i[1] for i in picked_regexes]

   # for i in picks:
    #    picked_regexes.append(config.regex_array[i - 1])

    if (start_date is not None):
        print("Picked start date", start_date.strftime(config.timestring))
    if (end_date is not None):
        print("Picked end", end_date.strftime(config.timestring))

    result = config.feeds.first_occurrences(regexpatterns, start_date, end_date)

    print("\n=== First occurence(s) of " + ', '.join(regexnames) + " ===")
    if (start_date is not None):
        print("Starting at", start_date.strftime(config.timestring))
    if (end_date is not None):
        print("Ending at", end_date.strftime(config.timestring))
        print("")


    # as a mind-bending exercise, try to rewrite the loop below with list comprehensions. :)
    sheet_output = []

    for i in range(0,len(result)):

        item = result[i]
        # item is of the format [ALog, first occurrence of A, first occurrence of B, ...]

        next_line = [(nonestring if x is None else x.strftime(timestring)) for x in item[1:]]
        print(next_line)
        print(item[0].username + ": " + ', '.join(next_line))

        sheet_output.append([result[i][0].username] + next_line)


    if(sheet_id is not None):
        credentials = get_credentials()
        http = credentials.authorize(httplib2.Http())
        discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                        'version=v4')
        service = discovery.build('sheets', 'v4', http=http,
                                  discoveryServiceUrl=discoveryUrl)

        spreadsheetId = sheet_id

        values = [
                     ["Player"] + [i[0] for i in picked_regexes]
        ] + sheet_output

        data = [
            {
                'range': startingCell,
                'values': values
            }
            # Additional ranges to update ...
        ]
        body = {
            'valueInputOption': "USER_ENTERED",
            'data': data
        }

        result = service.spreadsheets().values().batchUpdate(
            spreadsheetId=spreadsheetId, body=body).execute()

        print("Total updated cells in spreadsheet: {0}".format(result["totalUpdatedCells"]))


elif(sys.argv[1].lower()=="regexes"):
    print("=== Regex options ===")
    for i in range(0, len(config.regex_array)):
        print(str(i + 1) + ". " + config.regex_array[i][0])
else:
    print_help()
