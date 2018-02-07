import os
import config
from adventurerlog import AdventurerLog
from adventurerlog import AdventurerLogEvent
from adventurerlog import ALogUpdateResult
from datetime import datetime

import re
import json
import requests


def log(s):
    print(s)
class FeedUpdateResult(object):
    def __init__(self, new_entries, messages):
        """

        :param new_entries: The count of new entries
        :param warning_messages: The list of warning messages
        """
        self.new_entries = new_entries
        self.messages = messages
class FeedObject(object):
    #players list
    #logs list
    #name



    def __init__(self,feedname,logs):
        self.feedname = feedname
        self.logs = logs
        self.lastUpdated = datetime.utcnow()

    def count_matches(self,regex,start_date,end_date,skipzero = False):
        """

        :param regex:
        :param start_date:
        :param end_date:
        :return: A list of lists with format: [username, matches count]
        """
        output = []
        for log in self.logs:
            result = log.count_matches(regex,start_date,end_date)
            if((not skipzero) or result != 0):
                output.append([log,result])

        return output
    def first_occurrences(self,regex_patterns,start_date,end_date):
        """

        :param regex:
        :param start_date:
        :param end_date:
        :return: A list of lists with format: [username, first occurrence of 1, ...]
        """
        output = []
        for log in self.logs:
            result = log.first_occurrences(regex_patterns,start_date,end_date)
            output.append([log]+result)

        return output

    def update(self):
        """
        Returns a list of ALogUpdateResult , for each individual adventurer log.
        """
        results = []
        for log in self.logs:
            print("Updating {0}...".format(log.username))
            try:
                results.append(log.update())
            except KeyError as ex:
                results.append(ALogUpdateResult(log.username, 0, ["Error - Log for this user is not found."]))
            except Exception as ex:
                results.append(ALogUpdateResult(log.username,0,["Error - {0}".format(ex)]))
        self.lastUpdated = datetime.utcnow()
        return results

    def add_player(self,username):
        #check if player exists
        for log in self.logs:
            if(log.username == username):
                raise KeyError("Log for player {0} already exists.".format(username))

        nextlog = AdventurerLog(username,[])

        self.logs.append(nextlog)

    @staticmethod
    def init_feed():
        curdir = config.default_feed_dir
        if(os.path.isfile(curdir)):
            raise Exception("File with the feed name exists, while attempting to create folder")
        elif(os.path.isdir((curdir))):
            return FeedObject.open_feed(config.default_feed_name,curdir)
        else:
            return FeedObject.create_feed(config.default_feed_name, curdir)
    @staticmethod
    def open_feed(name,path):
        """
        Opens a feed in the SPECIFIED DIRECTORY
        (with a given name)
        """
        logs=[]

        f = open(os.path.join(path,config.playerfile),"r")
        players = f.readlines()
        f.close()

        for player in players:

            player = player.rstrip()
            if(len(player)==0):
                continue
            newpath = os.path.join(path, player+config.logext)

            #create the playerfile if it does not exist.
            if os.path.isdir(newpath):
                raise Exception("A folder is found, when trying to create playerfile of the same name.")
            elif not os.path.isfile(newpath):
                playerfile = open(newpath,"w+")
                playerfile.write(player+"\n")
                playerfile.close()

            log = AdventurerLog.loadfromfile(newpath)
            logs.append(log)#config.feed_prefix+name,

        #print("opened repository ")

        return FeedObject(name,logs)

    def save_feed(self,path):
        f = open(os.path.join(path, config.playerfile), "w+")
        for alog in self.logs:
            alog.savetofile(os.path.join(path, alog.username + config.logext))
            f.write(alog.username+"\n")
            #print(alog.username,"saved")
        f.close()


        #print("saved repository")
    @staticmethod
    def create_feed(name,path):
        """
        Creates and returns a feed in the SPECIFIED DIRECTORY.
        (with a given name).
        Raises errors as needed.
        """
        curdir = os.path.join(path)
        playersfile = os.path.join(curdir,config.playerfile)
        if(os.path.isdir(curdir)):
            raise Exception("Folder already exists while attempting to create this feed")
        os.mkdir(curdir)
        if(not os.path.isfile(playersfile)):
            open(playersfile ,"w+").close()
        log("created repository "+name)

        return FeedObject(config.default_feed_name,[])

    @staticmethod
    def list_feed_names():
        feed_names = []
        for name in os.listdir(config.workdir):
            if(os.path.isdir(name) and len(name)>len(config.feed_prefix) and name.startswith("feed_")):
                feed_names.append(feed_names)

        return feed_names


#date details text
"""
-update feeds
-analyze feeds
-store feeds...
"""
