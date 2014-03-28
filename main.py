__author__ = 'Cesar'

import config
config.logging.info("------------------START-------------------")


import threading
import comunicacionG4
import actuaEventos
import adquiereEventos
import verificaRelojSistema
import time

config.logging.info("-------------Starting Threads-------------")
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
# Start Serial Coms Daemon
serialDaemon = threading.Thread(target=comunicacionG4.serialDaemon)
serialDaemon.daemon = True
serialDaemon.start()
time.sleep(.5)
# Start Time Verification Daemon
verificaTiempoDaemon = threading.Thread(target=verificaRelojSistema.comparaTiempos)
verificaTiempoDaemon.daemon = True
verificaTiempoDaemon.start()
time.sleep(.5)
config.logging.info("---------Starting Threads Done!-----------")

while True:
    try:
        a = 0
    except Exception as e:
        config.logging.error("main: Unexpected exception - {}".format(e))
