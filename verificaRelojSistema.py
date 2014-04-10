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
            while not comunicacionG4.tiempoEscDisponible():
                tiempoG4 = time.mktime(comunicacionG4.getTiempoEsc())
                config.logging.debug("verificaRelojSistema: tiempoEsc -> [{0}]"
                                     .format(time.strftime('%H:%M:%S %d/%m/%Y', comunicacionG4.getTiempoEsc())))
                tiempoSys = time.mktime(time.localtime())
                config.logging.debug("verificaRelojSistema: tiempoSys -> [{0}]"
                                     .format(time.strftime('%H:%M:%S %d/%m/%Y', time.localtime())))
                # mqtt client loop for watchdog keep alive
                config.logging.info("verificaRelojSistema: Watchdog Keep Alive - Esperando TiempoEsc")
                # mqtt loop takes 1 sec to execute
                mqttcWC.loop()

            config.logging.info("verificaRelojSistema: TiempoEsc Disponible!")

            r = os.system('ntpdate {0}'.format(config.ntpserver))
            if r == 0:
                config.logging.info("verificaRelojSistema: ntpdate command successful, time updated")
                if not comunicacionG4.tiempoEscValido():
                    config.logging.warning("verificaRelojSistema: Reloj ESC invalido - Corrigiendo")
                    comunicacionG4.setTiempoEsc()
                elif tiempoSys > tiempoG4+120 or tiempoSys < tiempoG4-120:
                    config.logging.info("verificaRelojSistema: Reloj ESC valido, tiempo incorrecto - Corrigiendo")
                    comunicacionG4.setTiempoEsc()
            else:
                config.logging.info("verificaRelojSistema: ntpdate command failed, time uncertain")
                if tiempoSys > tiempoG4+120 or tiempoSys < tiempoG4-120:
                    config.logging.warning("verificaRelojSistema: Corrigiendo reloj RaspberryPi")
                    os.system('date -s \'@{0}\''.format(tiempoG4))

            t = 0
            while t < config.actualizaReloj:
                # mqtt client loop for watchdog keep alive
                config.logging.debug("verificaRelojSistema: Watchdog Keep Alive")
                # mqtt loop takes 1 sec to execute
                mqttcWC.loop()
                t += 1

        except Exception as e:
            config.logging.error('verificaRelojSistema: Error en Verificar Tiempos - {0}'.format(e))