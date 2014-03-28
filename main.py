__author__ = 'Cesar'

import config
config.logging.info("------------------START-------------------")


import threading
import comunicacionG4
import actuaEventos
import adquiereEventos
import verificaRelojSistema


# Start Adquiere Eventos Daemon
adquiereEventosDaemon = threading.Thread(target=adquiereEventos.adquiereEventos)
adquiereEventosDaemon.daemon = True
adquiereEventosDaemon.start()
# Start Actua Eventos Daemon
actuaEventosDaemon = threading.Thread(target=actuaEventos.actuaEventos)
actuaEventosDaemon.daemon = True
actuaEventosDaemon.start()
# Start Serial Coms Daemon
serialDaemon = threading.Thread(target=comunicacionG4.serialDaemon)
serialDaemon.daemon = True
serialDaemon.start()
# Start Time Verification Daemon
verificaTiempoDaemon = threading.Thread(target=verificaRelojSistema.comparaTiempos)
verificaTiempoDaemon.daemon = True
verificaTiempoDaemon.start()

while True:
    a = 0

