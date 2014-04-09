__author__ = 'Cesar'

import config
import getIP
config.logging.info("------------------WAIT-------------------")
getIP.waitForIP()

import threading
import comunicacionG4
import actuaEventos
import adquiereEventos
import verificaRelojSistema
import time

config.logging.info("-------------Starting Threads-------------")
lock = threading.Lock()

# Start Serial Coms Daemon
serialDaemon = threading.Thread(target=comunicacionG4.serialDaemon)
serialDaemon.daemon = True
serialDaemon.start()
time.sleep(.5)

# Wait for Clock
config.logging.info("  ----> Wait for Clock <----  ")
while time.mktime(time.localtime()) < 946706400:
    # Time is less than 01/01/2000
    config.logging.debug('Time not updated yet!')
    time.sleep(1)
config.logging.info("  ----> Clock updated: {0} <----  "
                    .format((time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))))

# Start Time Verification Daemon
verificaTiempoDaemon = threading.Thread(target=verificaRelojSistema.comparaTiempos)
verificaTiempoDaemon.daemon = True
verificaTiempoDaemon.start()
time.sleep(.5)


# Start Adquiere Eventos Daemon
adquiereEventosDaemon = threading.Thread(target=adquiereEventos.adquiereEventos)
adquiereEventosDaemon.daemon = True
adquiereEventosDaemon.start()
time.sleep(.5)
# Start Actua Eventos Daemon
actuaEventosDaemon = threading.Thread(target=actuaEventos.actuaEventos)
actuaEventosDaemon.daemon = True
actuaEventosDaemon.start()
time.sleep(.5)
config.logging.info("---------Starting Threads Done!-----------")

while True:
    try:
        a = 0
    except Exception as e:
        config.logging.error("main - Unexpected Error! - {}".format(e))
