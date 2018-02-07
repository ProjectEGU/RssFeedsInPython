from datetime import datetime
import config
import os
import requests
import json
import re

class AdventurerLog(object):

    def __init__(self, username,events_list):
        self.lastUpdated = datetime.utcnow()
        self.username = username
        self.events = events_list
        pass

    @staticmethod
    def loadfromfile(path):
        """
        :return:
        """
        username = ""
        events = []

        f = open(path,"r")
        username = f.readline().rstrip()
        for line in f.readlines():
            line = line.rstrip()
            if(len(line)==0):
                continue
            evt=AdventurerLogEvent.FromFileString(line)
            events.append(evt)

            #evt.username == username #make sure this is true! so we don't mess it up
            #oh but USERNAME CHANGES how do we deal with that shit.
        f.close()

        return AdventurerLog(username,events)
    def savetofile(self,path):
        """
        Creates or overwrites a file
        :param path:
        :return:
        """
        f = open(path,"w+")

        f.write(self.username+"\n")
        for evt in self.events:
            f.write(evt.ToFileString()+"\n" )

        f.close()

    @staticmethod
    def get_events(username):
        output = []

        j = requests.get(
            "https://apps.runescape.com/runemetrics/profile/profile?user={0}&activities=20".format(username))
        #  the [2:-1] removes the b'' wrapper. replace \' escapes because those fuck up the python json reader.
        j_filt = str(j.content)[2:-1].replace("\\'", "'")
        j_obj = json.loads(j_filt)
        try:
            for obj in j_obj["activities"]:
                date = datetime.strptime(obj["date"], config.jsontimestring)
                title = obj["text"]
                description = obj["details"]
                output.append(AdventurerLogEvent(username, date, title, description))
            output.reverse()
        except Exception as ex:
            pass

        return output

    @staticmethod
    def find_lowest_index(events, new_events):
        def confirm_match(current_events, new_events, i):
            # subfunction returns false if a mismatch was encountered, otherwise true
            for j in range(i, min(i+len(new_events),len(current_events))):
                t = j-i
                if(current_events[j] != new_events[t]):
                    return False
            return True

        lowest_match_index = -1

        for i in range(len(events) - 1, -1, -1):
            if (confirm_match(events, new_events, i)):
                lowest_match_index = i
            # continue searching until the date of the old event is before this new event
            # this fix is to prevent duplicates from fucking up the log. and yes, we do have duplicates sometimes.
            if events[i].date < new_events[0].date:
                break

        return lowest_match_index

    def update(self):
        event_c = 0
        warnings =  []

        new_events = self.get_events(self.username)

        if(len(new_events)==0):
            warnings.append("Did not get feeds from this user. ".format(self.username))
            return ALogUpdateResult(self.username, event_c, warnings)

        lowest_match_index = self.find_lowest_index(self.events, new_events)

        if (lowest_match_index == -1):
            if(len(self.events) > 0):
                warnings.append(
                    "Did not find matching event between current store log and new data. There may be lost events due to infrequent synch.")
            lowest_match_index = len(self.events)

        idx = len(self.events)-lowest_match_index
        event_c = len(new_events) - idx

        # print("new events: ",len(new_events) , ", lowest_match_idx = ",lowest_match_index ,
        #       ", len(self.events) = ",len(self.events),", idx = ",idx,sep = "")
        # TODO - find the other type of paradox, involving the date mismatching
        if(idx>len(new_events)): # equivalently, if event_c < 0.
            warnings.append("A paradox has been detected, and nothing was updated. There may be tampering with the current store log.")
            idx = 0
            event_c = 0
        else:
            self.events += new_events[idx:] #beautiful one liner to combine the lists

            self.lastUpdated = datetime.utcnow()

        return ALogUpdateResult(self.username, event_c, warnings)


    def count_matches(self, regex,start_date,end_date):
        """
        Rules for parsing the regex

        - The "Description" of the event will be what's subject to matching.

        - The first matched group will be split into spaces, and
        the first element will be converted to an integer.
        This will be added to the total sum, if successful.

        - The capturing group shall be counted as 1 if there is a match
        and it cannot be converted to an integer in the method specified above
        :param regex:
        :return:
        """
        output = 0
        for evt in self.events:
            s = evt.description
            matchobj = re.findall(regex, s, re.MULTILINE)

            delta = 0 # a debug variable that says how much the output should increase by, this iteration.

            if(matchobj): # a match has been found, we need to figure out how much it counts for.

                # check that the event is after start datetime
                begin = True if start_date is None else evt.date >= start_date

                # check that the event is before end datetime
                end = True if end_date is None else evt.date <= end_date

                # this print below is no longer necessary, i believe. we know the date matching works.
                #print("[DEBUG]",evt.date.strftime(config.jsontimestring),
                #      "None" if start_date is None else start_date.strftime(config.jsontimestring),
                #      "None" if end_date is None else end_date.strftime(config.jsontimestring),begin,end)

                if(begin and end): #
                    if(len(matchobj)==1): # there is exactly one capturing group
                        try:
                            next = matchobj[0].split(' ')[0]
                            if(len(next)==0 or not next[0].isdigit()):
                                delta = 1 # could not convert the capturing group to an integer
                            else:
                                delta = int(next) # converted the capturing group to an integer
                        except Exception:
                            print("[Debug]","exception converting data")
                            delta = 1
                    else:
                        delta = 1 # matched without a capturing group
            output += delta

            print("[DEBUG]", self.username, s, matchobj,delta) # this line spams the shit outta me
        return output
    def first_occurrences(self, regexpatterns, start_date, end_date):
        """
        
        :param regexpatterns: A list of regex match patterns.
        :param start_date: 
        :param end_date: 
        :return: A list of datetimes corresponding to the first match of the regex. If there's a None, then it wasn't found.
        """
        output = [None] * len(regexpatterns)

        for evt in self.events:
            s = evt.description


            begin = True if start_date is None else evt.date >= start_date

            end = True if end_date is None else evt.date <= end_date

            if(begin and end): #
                for i in range(0,len(regexpatterns)):
                    if(output[i] is not None):
                        continue

                    regex = regexpatterns[i]
                    matchobj = re.findall(regex, s, re.MULTILINE)
                    if (matchobj):
                        # a match has been found - we assume that the events list is in chronological order,
                        # so we directly replace the event.
                        output[i] = evt.date

                        print("[DEBUG]",evt.title,

                             evt.date.strftime(config.jsontimestring),
                             "None" if start_date is None else start_date.strftime(config.jsontimestring),
                             "None" if end_date is None else end_date.strftime(config.jsontimestring),

                              begin,end,sep='|')

                        #print("[DEBUG]", self.username, s, matchobj) # this line spams the shit outta me
        return output
class AdventurerLogEvent(object):
    def __init__(self, username, date, title, description):
        self.username = username
        self.date_retrieved = datetime.utcnow()
        self.title = title

        self.description = description
        self.date = date

    def __eq__(self, other):
        return self.username == other.username \
            and self.title == other.title \
            and self.description == other.description \
            and self.date == other.date

    def __str__(self):
        return "{0:<15}{1:<50}{2:<50}".format(
            self.date.strftime(config.timestring),
            self.title,
            self.description)

    def ToFileString(self):
        return "|".join([self.username,
                         self.date.strftime(config.jsontimestring),
                         self.title,
                         self.description,
                         self.date_retrieved.strftime(config.jsontimestring)])

    @staticmethod
    def FromFileString(datastring):
        data = datastring.split("|")

        username = data[0]
        date = datetime.strptime(data[1],config.jsontimestring)
        title = data[2]
        description = data[3]
        date_retrieved = datetime.strptime(data[4],config.jsontimestring)

        evt = AdventurerLogEvent(username,date,title,description)
        evt.date_retrieved = date_retrieved #wasting that datetime.utcnow() call in the constructor

        return evt
class ALogUpdateResult(object):
    def __init__(self, username,new_entries, warning_messages):
        self.username = username
        self.new_entries = new_entries
        self.warning_messages = warning_messages
"""
f = open("adhd","w+")

f.write("a\n")
f.write("b\n")
f.write("c\n")

f.close()
f=open("adhd","r")
print(f.readline())
print(f.readline())
print(len(f.readline().rstrip()))
print(len(f.readline()))
print(len(f.readline()))
f.close()"""
"""
new_events = []

j = requests.get("https://apps.runescape.com/runemetrics/profile/profile?user={0}&activities=20".format("chaoster7"))
j_filt = str(j.content)[2:-1].replace("\\'", "'")
j_obj = json.loads(j_filt)
for obj in j_obj["activities"]:
    date = datetime.strptime(obj["date"], "%d-%b-%Y %H:%M")
    title = obj["text"]
    description = obj["details"]
    new_events.append(AdventurerLogEvent("chaoster7",date,title,description))

for evt in new_events:
    print(evt.date,evt.title,evt.description)

"""
#for name in os.listdir("."):
#    print(name,os.path.isdir(name))
#d = datetime.utcnow()
#d=datetime.strptime("2017-02-23 @ 02:27", "%Y-%m-%d @ %H:%M")
#d2 =datetime.strptime("2017-02-23 @ 02:21", "%Y-%m-%d @ %H:%M")
#print(d.strftime(config.timestring))
#print(d==d2)
"""
title
description
date on record


username
date retrieved

"""
"""
        from tkinter import Tk
        r = Tk()
        r.withdraw()
        #r.clipboard_clear()
        #r.clipboard_append('i can has clipboardz?')
        k = r.clipboard_get()
        print(k)
        r.destroy()
        import urllib.request
        with urllib.request.urlopen('https://apps.runescape.com/runemetrics/profile/profile?user=chaoster7&activities=20') as response:
           html = response.read()
        print(html)

        config.players = "a"

        feedupdater.b()

        print(config.players)
        config.players="k"
        feedupdater.c()
        """
""" TODO - use the magical one liner here
for i in range(0,len(new_events)):
    t = i + lowest_match_index
    if(t>=len(self.events)):
        self.events.append(new_events[i])
        event_c += 1
    else:
        #print("[DEBUG]",t,len(self.events),i,len(new_events))
        if self.events[t]!=new_events[i]:
            warnings.append("Mismatched event: " + str(self.events[t])+", "+str(new_events[i]))
"""