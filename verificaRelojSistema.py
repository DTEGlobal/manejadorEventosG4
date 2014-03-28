__author__ = 'Cesar'

import config

import time
import comunicacionG4
import os

def comparaTiempos():
    config.logging.info("verificaRelojSistema: comparaTiempos Thread Running ...")
    while True:
        try:
            time.sleep(10)
            tiempoG4 = time.mktime(comunicacionG4.getTiempoEsc())
            tiempoSys = time.mktime(time.localtime())
            if tiempoSys > tiempoG4+120 or tiempoSys < tiempoG4-120:
                os.system('date -s \'@{0}\''.format(tiempoG4))
            time.sleep(config.actualizaReloj)
        except:
            config.logging.error('Error en Verificar Tiempos')


