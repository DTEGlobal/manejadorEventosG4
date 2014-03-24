# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Command-line skeleton application for Calendar API.
Usage:
  $ python sample.py

You can also get help on all the command-line flags the program understands
by running:

  $ python sample.py --help

"""

import argparse
import httplib2
import os
import sys

import time

from apiclient import discovery
from oauth2client import file
from oauth2client import client
from oauth2client import tools

# Parser for command-line arguments.
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[tools.argparser])


# CLIENT_SECRETS is name of a file containing the OAuth 2.0 information for this
# application, including client_id and client_secret. You can see the Client ID
# and Client secret on the APIs page in the Cloud Console:
# <https://cloud.google.com/console#/project/949645467864/apiui>
CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'client_secrets.json')

# Set up a Flow object to be used for authentication.
# Add one or more of the following scopes. PLEASE ONLY ADD THE SCOPES YOU
# NEED. For more information on using scopes please see
# <https://developers.google.com/+/best-practices>.
FLOW = client.flow_from_clientsecrets(CLIENT_SECRETS,
                                      scope=[
                                          'https://www.googleapis.com/auth/calendar',
                                          'https://www.googleapis.com/auth/calendar.readonly',
                                      ],
                                      message=tools.message_if_missing(CLIENT_SECRETS))


def main(argv):
    # Parse the command-line flags.
    flags = parser.parse_args(argv[1:])

    # If the credentials don't exist or are invalid run through the native client
    # flow. The Storage object will ensure that if successful the good
    # credentials will get written back to the file.
    storage = file.Storage('sample.dat')
    credentials = storage.get()
    if credentials is None or credentials.invalid:
      credentials = tools.run_flow(FLOW, storage, flags)

    # Create an httplib2.Http object to handle our HTTP requests and authorize it
    # with our good Credentials.
    http = httplib2.Http()
    http = credentials.authorize(http)

    # Construct the service object for the interacting with the Calendar API.
    service = discovery.build('calendar', 'v3', http=http)

    try:
        deviceName = service.calendarList().get(calendarId='primary').execute()['id']
        calendar_list = service.calendarList().list().execute()
        current_date = time.mktime(time.localtime())
        timeMin = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.localtime(current_date))
        timeMax = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.localtime(current_date + 30*86400))
        print ('{0} - {1}'.format(timeMin, timeMax))

        for calendar in calendar_list['items']:
            accion, estado = calendar['summary'].split(':')

            print ("Device name = [{0}]\n"
                   "Accion = [{1}]\n"
                   "Estado = [{2}]".format(deviceName, accion, estado))

            current_month_events = service.events().list(calendarId=calendar['id'],
                                                         singleEvents=True,
                                                         timeMax=timeMax,
                                                         timeMin=timeMin).execute()
            for current_event in current_month_events['items']:
                try:
                    s = current_event['start']['dateTime']
                    date, t = s.split('T')
                    t, q = t.split('-')
                    start = '{0} {1}'.format(date, t)
                    e = current_event['end']['dateTime']
                    date, t = e.split('T')
                    t, q = t.split('-')
                    end = '{0} {1}'.format(date, t)
                    print("\tStart = [{0}]\n\tEnd = [{1}]".format(start, end))
                except KeyError:
                    print ("\t(All Day Event)\n\t\tStart = [{1}]\n\t\tEnd = [{2}]"
                           .format(current_event['summary'],
                                   current_event['start']['date'],
                                   current_event['end']['date']))

    except client.AccessTokenRefreshError:
        print ("The credentials have been revoked or expired, please re-run"
               "the application to re-authorize")


if __name__ == '__main__':
    main(sys.argv)
