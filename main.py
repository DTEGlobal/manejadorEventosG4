__author__ = 'Cesar'

import config
import threading
import time

import comunicacionG4
import verificaRelojSistema
import actuaEventos
import adquiereEventos
import ping

config.logging.info("-------------Starting Threads-------------")
lock = threading.Lock()

time.sleep(30)

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

# Wait for Clock
config.logging.info("  ----> Wait for Clock <----  ")
while time.mktime(time.localtime()) < 946706400:
    # Time is less than 01/01/2000
    config.logging.debug('main: Time not updated yet!')
    time.sleep(1)
config.logging.info("  ----> Clock updated: {0} <----  "
                    .format((time.strftime("%H:%M:%S %d/%m/%Y", time.localtime()))))

# Start Ping Daemon
killerDaemon = threading.Thread(target=ping.pingDaemon)
killerDaemon.daemon = True
killerDaemon.start()
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
        config.logging.error("main: Unexpected Error! - {}".format(e))
