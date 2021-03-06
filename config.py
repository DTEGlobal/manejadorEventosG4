__author__ = 'Cesar'


import logging
import threading

# Logging
logging.basicConfig(format='%(asctime)s - [%(levelname)s]: %(message)s',
                    filename='/home/logs/ManejadorEventosG4.log',
                    level=logging.INFO)

# Delays
delayAdquiereEventos = 600
delayActuaEventos = 30
delayAdquiereEventosRetry = 120
delaySerial = 1

# Amount of events to store locally (days)
daysToStoreLocally = 60
secondsToStoreLocally = daysToStoreLocally * 86400

# Time interval between clock verification
actualizaReloj = 3600

# NTP Server
ntpserver = 'pool.ntp.org'

# Thread lock
lock = threading.Lock()

#wireless adapter detection
delayPing = 300

#seconds without network connection before reboot
rebootCount = 5
