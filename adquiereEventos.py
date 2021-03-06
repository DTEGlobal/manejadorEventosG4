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
  $ python testCalendar.py

You can also get help on all the command-line flags the program understands
by running:

  $ python testCalendar.py --help

"""
import config
import argparse
import httplib2
import os
import MySQLdb
import time
import mosquitto
import ping

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

# Create Mosquitto Client for Watchdog broker
mqttcWC = mosquitto.Mosquitto("adquiereEventosWC")


def on_connect_aeWC(mosq, obj, rc):
    config.logging.info("adquiereEventos: adquiereEventos Watchdog Client connected")
    mqttcWC.subscribe("#", 0)


def adquiereEventos():
    config.logging.info("adquiereEventos: adquiereEventos Thread Running ...")
    # Connect to mqtt watchdog server
    mqttcWC.on_connect = on_connect_aeWC
    mqttcWC.connect('localhost', 1884)
    connection_successful = True

    while True:
        try:
            try:
                # Parse the command-line flags.
                flags = parser.parse_args('')
                # If the credentials don't exist or are invalid run through the native client
                # flow. The Storage object will ensure that if successful the good
                # credentials will get written back to the file.
                credentials = None
                storage = None
                samplePath = os.path.join(os.path.dirname(__file__), 'sample.dat')
                config.logging.info("  ----> Wait for Credentials file: sample.dat <----  ")
                get_sample_dat_counter = 0
                while credentials is None:
                    storage = file.Storage(samplePath)
                    credentials = storage.get()
                    time.sleep(1)
                    if get_sample_dat_counter > 3:
                        config.logging.error(" adquiereEventos: {0} Try to get sample.dat .. Fail! =S"
                                             .format(get_sample_dat_counter))
                        break
                    else:
                        get_sample_dat_counter += 1
                        config.logging.warning(" adquiereEventos: {0} Try to get sample.dat  "
                                               .format(get_sample_dat_counter))
                if credentials is not None:
                    config.logging.info("  ----> Credentials file Acquired! <----  ")
                    if credentials.invalid:
                        # credentials = tools.run_flow(FLOW, storage, flags)
                        config.logging.warning("adquiereEventos: Invalid credentials detected in sample.dat =(")
                        credentials.invalid = False
                        storage.put(credentials)
                        config.logging.warning("adquiereEventos: Stored [Invalid = False] in sample.dat!!")
                    else:
                        config.logging.info("adquiereEventos: Valid credentials detected in sample.dat =)")

                    # Create an httplib2.Http object to handle our HTTP requests and authorize it
                    # with our good Credentials.
                    http = httplib2.Http()
                    http = credentials.authorize(http)

                    # Construct the service object for the interacting with the Calendar API.
                    service = discovery.build('calendar', 'v3', http=http)

                    with config.lock:
                        # Construct DB object
                        db = MySQLdb.connect(host='localhost', user='root', passwd='petrolog', db='eventosg4')
                        cursor = db.cursor(MySQLdb.cursors.DictCursor)

                        # Primary calendar id includes the device name (ei. sofi.compresor1@gmail.com)
                        deviceName = service.calendarList().get(calendarId='primary').execute()['id']
                        calendar_list = service.calendarList().list().execute()

                        # Get current date and configuration to calculate dates to pull from calendar
                        current_date = time.mktime(time.localtime())
                        timeMin = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.localtime(current_date))
                        timeMax = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.localtime(current_date
                                                                                     + config.secondsToStoreLocally))
                        timeCurrent = time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(current_date))
                        config.logging.debug('Dates to get: {0} - {1}'.format(timeMin, timeMax))

                        # Clear event table
                        cursor.execute('DELETE from eventos WHERE idEventos > 0')
                        for calendar in calendar_list['items']:
                            accion, estado = calendar['summary'].split(':')
                            config.logging.info("Device name = [{0}], "
                                                "Accion = [{1}], "
                                                "Estado = [{2}]".format(deviceName, accion, estado))
                            cursor.execute('SELECT * FROM dispositivo')
                            currentName = cursor.fetchone()
                            if currentName['nombre'] != deviceName:
                                config.logging.debug('si necesitamos cambio de nombre!')
                                cursor.execute('UPDATE dispositivo SET nombre = \'{0}\''.format(deviceName))

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
                                    config.logging.info("Start = [{0}], "
                                                        "End = [{1}]".format(start, end))
                                    cursor.execute('INSERT into eventos '
                                                   'VALUES (NULL, \'{0}\', \'{1}\', \'{2}\', \'{3}\', \'01\', \'{4}\')'.
                                                   format(start,
                                                          end,
                                                          accion,
                                                          estado,
                                                          timeCurrent))
                                except KeyError:
                                    start = current_event['start']['date']+' 00:00:00'
                                    end = current_event['end']['date']+' 23:59:59'
                                    config.logging.debug("(All Day Event)"
                                                         "Start = [{1}]"
                                                         "End = [{2}]"
                                                         .format(current_event['summary'], start, end))
                                    cursor.execute('INSERT into eventos '
                                                   'VALUES (NULL, \'{0}\', \'{1}\', \'{2}\', \'{3}\', \'01\', \'{4}\')'.
                                                   format(start,
                                                          end,
                                                          accion,
                                                          estado,
                                                          timeCurrent))
                        db.commit()
                        cursor.close()
                        db.close()
                        connection_successful = True
            except client.AccessTokenRefreshError:
                config.logging.critical("The credentials have been revoked or expired, please re-run"
                                        "the application to re-authorize")
                try:
                    config.lock.release()
                except:
                    config.logging.info('adquiereEventos: Lock already released')

            except httplib2.ServerNotFoundError:
                #config.logging.warning("No internet access retry in {0} sec".format(config.delayAdquiereEventos))
                config.logging.warning("No internet access retry in 60 sec")
                connection_successful = False

                try:
                    config.lock.release()
                except:
                    config.logging.info('adquiereEventos: Lock already released')

        except Exception as e:
            config.logging.error('adquiereEventos: Unexpected Error! - {0}'.format(e.message))
            try:
                config.lock.release()
            except:
                config.logging.info('adquiereEventos: Lock already released')

        t = 0
        # If can't connect to google retry in delayAdquiereEventosRetry.
        if connection_successful is False:
            Delaytime = config.delayAdquiereEventosRetry
        else:
            Delaytime = config.delayAdquiereEventos

        while t < Delaytime or ping.raspberrypiKiller == 1:
            if ping.raspberrypiKiller == 1:
                config.logging.info("adquiereEventos: Ready for Shutdown")
                ping.killerArray[2] = True
                while True:
                    a = 0
            # mqtt client loop for watchdog keep alive
            config.logging.debug("adquiereEventos: Watchdog Keep Alive")
            mqttcWC.loop(0)
            time.sleep(1)
            t += 1
