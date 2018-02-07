import feedobject
import os
jsontimestring = "%d-%b-%Y %H:%M"
timestring = "%Y-%m-%d @ %H:%M [%I:%M %p] %Z" # %Z is supposed to be the timezone, but it doesnt do shit here.
players = []
workdir = "."
feed_prefix = "feed_"

feeds = None

default_feed_name="all"

playerfile = "_players.txt"

logext=".txt"#extension for adventurer log files

default_feed_dir= os.path.join(workdir,feed_prefix+default_feed_name)

#array of [regex name, regex pattern]
regex_array = []

regexfile = ".\\regex_patterns.txt"

selected_start_date=None
selected_end_date = None


updatelog = "update.log"