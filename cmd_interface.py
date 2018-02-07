import config
from feedobject import FeedObject
from tkinter import Tk
import os
from datetime import datetime

"""
TODO - seperate the two addplayers options into two main menu options
TODO - ways to delete players
TODO - regex analysis method
TODO - exportation methods to spreadsheet
TODO - database last updated

"""
def clear():
    os.system('cls')

"""
Return a value, or -1 if enter was pressed and accept_enter is true
"""
def get_int(prompt,min,max, accept_enter):
    while True:
        try:
            data = input(prompt)
            if(accept_enter and len(data)==0):
                return -1
            result = int(data)
            if(result >= min and result <= max):
                return result
        except Exception:
            pass

def getusername(prompt):
    """
    Gets a username. Returns the empty string if enter was pressed without any other input.
    :param prompt:
    :return:
    """
    while True:
        value = input(prompt)
        if(len(value)==0):
            return ""
        else:
            if(checkusername(value)):
                return value
            else:
                print("Invalid username: {0}\n".format(value))

def get_date(prompt,format):
    """
    Gets a date in a specified format. Returns None if enter was pressed without any other input

    :param prompt:
    :return:
    """
    while True:
        value = input(prompt)
        if (len(value) == 0):
            return None
        else:
            try:
                value = value.rstrip()
                output = datetime.strptime(value, format)
                return output
            except ValueError:
                print("Cannot parse time: {0}\n".format(value))
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
    result = config.feeds.update()
    print("=== Results ===")
    if(len(result)==0):
        print("(None)")
    else:
        new_entries = 0
        for item in result:
            new_entries += item.new_entries
            for msg in item.warning_messages:
                print("[{0}]: {1}".format(item.username,msg))
            print("[{0}]: {1} new items found".format(item.username,item.new_entries))
def SaveFeeds():
    curdir = config.default_feed_dir
    config.feeds.save_feed(curdir)
    print("Feeds saved. Press [ENTER] to continue. \n")
    input()
def AddPlayers():
    """
    :return: A list of warning/error messages.
    """
    while True:
        clear()
        print("=== Add Player options ===")
        print("")
        print("1. Add one by one")
        print("2. Paste from clipboard")
        print("3. Accept and go back")
        print("")
        print("To swap or remove players, please edit the players.txt file.\n")
        choice = get_int("Enter the choice >> ",1,3,False)
        if(choice == 1):
            while True:
                next = getusername("Enter a username to add, or [ENTER] to return to main menu >> ")
                if(len(next)==0):
                    return #return or break here?
                try:
                    config.feeds.add_player(next)
                    print("Added username: "+next)
                except KeyError as ex:
                    print("{0}".format(ex))
                except Error as ex:
                    raise
        elif choice == 2:
            r = Tk()
            r.withdraw()
            k = r.clipboard_get()
            r.destroy()
            for name in k.splitlines():
                try:
                    if(checkusername(name)):
                        config.feeds.add_player(name)
                    else:
                        print("Invalid username: {0}".format(name))
                except Exception as ex:
                    raise
                    print("Error - {0}".format(ex))


        elif choice == 3:
            return



def ListPlayers():
    while True:
        clear()
        print("=== List of Players ===")

        if(len(config.feeds.logs)==0):
            print("(None)")
            print("")
            print("Press [ENTER] to continue.")
            input()
            return

        print("")
        count = len(config.feeds.logs)
        for i in range(0,count):
            print((str(i+1)+".").ljust(5)+config.feeds.logs[i].username.ljust(20) + str(len(config.feeds.logs[i].events))+" events")
        print("")
        print("Enter a number to display the log, or press [ENTER] to exit.")

        print("")
        result = get_int(">> ",1,count,True)
        if(result == -1):
            return
        else:
            c=0
            for evt in config.feeds.logs[result-1].events:
                c+= 1
                print("{:<4}".format(c) + str(evt))
            print("")
            print("Press [ENTER] to return to player list.")
            print("Press [ENTER] twice to return to main menu.")
            input("\n")
def DataAnalyze():
    while 1:
        count = len(config.regex_array)

        print("Data Analyzer\n")
        print("=== Predefined options ===")
        for i in range(0,count):
            print(str(i+1)+". "+config.regex_array[i][0])
        print("")
        print("0. Custom Regex")
        print("")
        print("Press [ENTER] to go back.")
        print("")
        pick = get_int("Choose an option >> ",0,count,True)
        if(pick == 0):
            pass #TODO
        elif(pick==-1):
            break
        else:
            picked_regex = config.regex_array[pick-1]
                #so the month and day have to be 0 padded... and the hours is in 24h format...
            print("Enter the START date in 'YYYY-MM-DD hh:mm' format, or press [ENTER] for the beginning of time.")

            start_date = get_date(">> ","%Y-%m-%d %H:%M")
            if (start_date is not None):
                print("Picked start date", start_date.strftime(config.timestring))
            print("Enter the ENDING date in 'YYYY-MM-DD hh:mm' format, or press [ENTER] for the end of time.")

            end_date = get_date(">> ","%Y-%m-%d %H:%M")
            if(end_date is not None):
                print("Picked end",end_date.strftime(config.timestring))

            result = config.feeds.count_matches(picked_regex[1], start_date, end_date)
            print("\n=== Analysis of " + picked_regex[0]+" ===")
            if(start_date is not None):
                print("Starting at",start_date.strftime(config.timestring))
            if(end_date is not None):
                print("Ending at",end_date.strftime(config.timestring))
            for item in result:
                print(item[0].username+": " + str(item[1]))
            print("\nPress [ENTER] to continue. \n")
            input()
            return

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



InitRegex()

while True:
    clear()

    try:
        if(config.feeds is None):
            config.feeds = FeedObject.init_feed()
    except Exception as ex:
        print("Error while attempting to create feed: {0}".format(ex))
        raise
        break

    print("=== Player Adventurer Log Tracker ===")
    print("Players tracked:",len(config.feeds.logs))
    print("Opened: ",config.feeds.lastUpdated.strftime(config.timestring))
    print("")
    print("=== Options ===")
    print("1. Update events")
    print("2. Add players - from clipboard or manual entry")
    print("3. List players - view events")
    print("4. Analyze data - select date range")
    print("5. Exit")

    pick = get_int("Choose an option >> ",1,5,False)

    if(pick==1):


        UpdateCurrentEvents()

        SaveFeeds()
    elif(pick==2):
        AddPlayers()

        #UpdateCurrentEvents()
        SaveFeeds()
    elif(pick==3):
        ListPlayers()
    elif(pick==4):
        DataAnalyze()
    elif(pick==5):
        print("Exiting..")
        break



#########################
# CODE GRAVE LIES BELOW #
#########################

"""
while True:
    print(checkusername(input("\n")))
"""

#filestorage.load_config()


"""
print("=== Feed Collections ===\n")
    feeds = feedobject.list_feed_names()
    if len(feeds == 0):
        print("(None)")
    else:
        for i in range(0,len(feeds)):
            print(str(i+1)+". " + feeds[i][len(config.feed_prefix):])
    print("\n")

    pick = get_int("Enter an option >> ",0,5,accept_enter=False)

    if pick == 1:

        pass
    elif pick == 2:
        pass
    elif pick == 3:
        pass
    elif pick == 4:
        pass
"""