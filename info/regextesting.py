import re

#s = """I killed 10 Telos."""
s="""
[DEBUG] chaoster7 I killed 6 Araxxis. []
[DEBUG] chaoster7 I killed  a spinner of death, Araxxi. []
"""
#matchobj = re.findall(r"(spinner of death|\d+ Araxxi)",s,re.MULTILINE)
matchobj = re.findall(r"(?:(\d+) Araxxi)",s,re.MULTILINE)

if len(matchobj)>0:
    print(matchobj)
else:
    print("No match")