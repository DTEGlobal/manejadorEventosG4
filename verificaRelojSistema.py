__author__ = 'Cesar'
import time
import comunicacionG4
import os
import config

def comparaTiempos():
    while True:
        try:
            time.sleep(config.actualizaReloj)
            tiempoG4 = time.mktime(comunicacionG4.getTiempoEsc())
            tiempoSys = time.mktime(time.localtime())
            if tiempoSys > tiempoG4+120 or tiempoSys < tiempoG4-120:
                os.system('date -s \'@{0}\''.format(tiempoG4))

        except:
            config.logging.error('Error en Verificar Tiempos')


