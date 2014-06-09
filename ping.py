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
import comunicacionG4

# Create Mosquitto Client for Watchdog broker
mqttcWC = mosquitto.Mosquitto("pingWC")


def on_connect_pingWC(mosq, obj, rc):
    config.logging.info("ping: ping Watchdog Client connected")
    mqttcWC.subscribe("#", 0)

raspberrypiKiller = 0

def pingDaemon():
    global raspberrypiKiller

    raspberrypiKiller = 0

    config.logging.info("ping: Thread Running ...")
    # Connect to mqtt watchdog server
    mqttcWC.on_connect = on_connect_pingWC
    mqttcWC.connect('localhost', 1884)

    while True:

        config.logging.info("ping: Trying to ping default gateway")
        pingResult = os.popen("ping -c 1 192.168.1.254").read()
        pingMatch = re.search(', 1 received', pingResult)
        if pingMatch != None:
            config.logging.info("ping: ping to default gateway successful")
            raspberrypiKiller = 0
        else:
            config.logging.critical("ping: No Network Connection")
            config.logging.info("ping: verifying usb port connection to wireless adapter")
            lsusbResult = os.popen("lsusb").read()
            lsusbMatch = re.search('Edimax.+Wireless', lsusbResult)
            if lsusbMatch != None:
                config.logging.info("ping: wireless adapter is detected")
                raspberrypiKiller = 0
            else:
                config.logging.critical("ping: wireless adapter is not detected")
                raspberrypiKiller = 1

                while config.killerArray != [True, True, True, True]:
                    time.sleep(0.5)
                    raspberrypiKiller = 1

                config.logging.critical("ping: ready to shutdown... powering off")
                time.sleep(1)
                comunicacionG4.SendCommand("01A60")
                os.popen("shutdown now")

        t = 0
        while t < config.delayPing:
            # mqtt client loop for watchdog keep alive
            config.logging.debug("ping: Watchdog Keep Alive")
            mqttcWC.loop(0)
            time.sleep(1)
            t += 1