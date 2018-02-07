import httplib2
import config

import os
from datetime import datetime

import sys

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

sheet_id = None
startingCell = 'A1'
date_format = config.jsontimestring
if(len(sys.argv)>=3):
    sheet_id = sys.argv[1]
    startingCell = sys.argv[2]
    if(len(sys.argv)>=4):
        date_format = sys.argv[3]
else:
    print("Usage - date_sheet.py sheet-id starting-cell [date-format]")
    print("First two arguments are required. For starting cell, A1 is the topleft cell.")
    print("For the date format, it is optional to provide it. Refer to python's strftime.")
    print("As an example, %H:%M will print out the date string in HH:MM format (24-hrs).")
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
            datetime.utcnow().strftime(date_format)
        ]

    ]

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
