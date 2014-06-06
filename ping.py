__author__ = 'Emmy'

#-------------------------------------------------------------------------------
# Name:        ping
# Purpose:
#
# Author:      Emmanuel
#
# Created:     06/05/2014
# Copyright:   (c) Petrolog 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import config
import time
import os
import re
import mosquitto

# Create Mosquitto Client for Watchdog broker
mqttcWP = mosquitto.Mosquitto("pingWC")


def on_connect_pingWC(mosq, obj, rc):
    config.logging.info("ping: ping Watchdog Client connected")
    mqttcWP.subscribe("#", 0)


def pingDeamon():

    raspberrypiKiller = 0

    config.logging.info("ping: Thread Running ...")
    # Connect to mqtt watchdog server
    mqttcWP.on_connect = on_connect_pingWC
    mqttcWP.connect('localhost', 1884)

    while True:

        config.logging.info("ping: Trying to ping default gateway")
        pingResult = os.popen("ping -c 1 192.168.1.254").read()
        pingMatch = re.search(', 1 received', pingResult)
        if pingMatch is True:
            config.logging.info("ping: ping to default gateway successful")
            raspberrypiKiller = 0
        else:
            config.logging.critical("ping: No Network Connection")
            config.logging.info("ping: verifying usb port connection to wireless adapter")
            lsusbResult = os.popen("lsusb").read()
            lsusbMatch = re.search('Edimax.+Wireless.+Realtek', lsusbResult)
            if lsusbMatch is True:
                config.logging.info("ping: wireless adapter is detected")
                raspberrypiKiller = 0
            else:
                config.logging.critical("ping: wireless adapter is not detected")

                raspberrypiKiller = 1

        t = 0
        while t < config.delayPing:
            # mqtt client loop for watchdog keep alive
            config.logging.debug("comunicacionG4: Watchdog Keep Alive")
            mqttcWP.loop(0)
            time.sleep(1)
            t += 1
