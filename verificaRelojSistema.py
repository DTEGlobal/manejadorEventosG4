__author__ = 'Cesar'

import config
import getIP
import time
import comunicacionG4
import os
import mosquitto

# Create Mosquitto Client for Watchdog broker
mqttcWC = mosquitto.Mosquitto("comparaTiemposWC")


def on_connect_ctWC(mosq, obj, rc):
    config.logging.info("verificaRelojSistema: comparaTiempos Watchdog Client connected")
    mqttcWC.subscribe("#", 0)


def comparaTiempos():
    config.logging.info("verificaRelojSistema: comparaTiempos Thread Running ...")
    # Connect to mqtt watchdog server
    mqttcWC.on_connect = on_connect_ctWC
    mqttcWC.connect(getIP.localaddress, 1884)

    while True:
        try:
            t = 0
            while t < config.actualizaReloj:
                # mqtt client loop for watchdog keep alive
                config.logging.debug("verificaRelojSistema: Watchdog Keep Alive")
                # mqtt loop takes 1 sec to execute
                mqttcWC.loop()
                t += 1

            tiempoG4 = time.mktime(comunicacionG4.getTiempoEsc())
            tiempoSys = time.mktime(time.localtime())
            if tiempoSys > tiempoG4+120 or tiempoSys < tiempoG4-120:
                os.system('date -s \'@{0}\''.format(tiempoG4))

        except Exception as e:
            config.logging.error('verificaRelojSistema: Error en Verificar Tiempos - {0}'.format(e))


