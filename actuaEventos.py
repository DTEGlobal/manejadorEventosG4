__author__ = 'Cesar'

import config
import MySQLdb
import mosquitto
import time

comando = ""

# Create Mosquitto Client for Watchdog broker
mqttcWC = mosquitto.Mosquitto("actuaEventosWC")


def on_connect_aeWC(mosq, obj, rc):
    config.logging.info("actuaEventos: actuaEventos Watchdog Client connected")
    mqttcWC.subscribe("#", 0)


def adquiereComando(estado):
    global comando
    # Construct DB object
    db = MySQLdb.connect(host='localhost', user='root', passwd='petrolog', db='eventosg4')
    # Traemos el Comando que toca dependiendo del estado en que se debe de encotrar el equipo
    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    campodb = ""
    if estado == 'Off':
        campodb = 'comandoApagado'
    elif estado == 'On':
        campodb = 'comandoEncendido'

    cursor.execute('SELECT {0} FROM dispositivo'.format(campodb))
    temp = cursor.fetchone()
    comando = temp['{0}'.format(campodb)]
    config.logging.debug('actuaEventos: Comando:{0}  Estado:{1}'.format(comando,estado))
    # Close DB object
    cursor.close()
    db.close()


def actuaEventos():
    config.logging.info("actuaEventos: actuaEventos Thread Running ...")
    # Connect to mqtt watchdog server
    mqttcWC.on_connect = on_connect_aeWC
    mqttcWC.connect('localhost', 1884)

    while True:
        try:
            with config.lock:
                # Construct DB object
                db = MySQLdb.connect(host='localhost', user='root', passwd='petrolog', db='eventosg4')
                cursor = db.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('SELECT accion, estado FROM eventos '
                               'WHERE fecha_inicio < now() and fecha_fin > now() '
                               'ORDER BY accion DESC, estado DESC')
                db.commit()
                queryResponse = cursor.fetchall()
                cursor.close()
                db.close()

            # Requirement: Activate output if no events found (by EC)
            state = 'On'
            accion = 'Normal'
            config.logging.debug(queryResponse)
            if len(queryResponse) > 1:
                config.logging.debug('actuaEventos: Eventos empalmados')
                for row in queryResponse:
                    if row['accion'] == 'Override':
                        accion = 'Override'
                        if row['estado'] == 'On':
                            state = 'On'
                            break
                        elif row['estado'] == 'Off':
                            state = 'Off'
                            break
                        else:
                            # TODO Rise error!
                            state = 'Error'
                    elif row['accion'] == 'Normal':
                        if row['estado'] == 'On':
                            state = 'On'
                            break
                        elif row['estado'] == 'Off':
                            state = 'Off'
                            break
                        else:
                            # TODO Rise error!
                            state = 'Error'
                    else:
                        # TODO Rise error!
                        state = 'Error'

            elif len(queryResponse) == 1:
                accion = queryResponse[0]['accion']
                config.logging.debug('actuaEventos: Un solo evento')
                if queryResponse[0]['estado'] == 'On':
                    state = 'On'
                elif queryResponse[0]['estado'] == 'Off':
                    state = 'Off'
                else:
                    # TODO Rise error!
                    state = 'Error'

            else:
                config.logging.debug('actuaEventos: No hay eventos programados para la hora actual')

            config.logging.info('actuaEventos: Accion:[{0}], Estado[{1}]'.format(accion, state))
            adquiereComando(state)

            t = 0
            while t < config.delayActuaEventos:
                # mqtt client loop for watchdog keep alive
                config.logging.debug("actuaEventos: Watchdog Keep Alive")
                # mqtt loop takes 1 sec to execute
                mqttcWC.loop()
                # mqtt returning immediately ????
                time.sleep(1)
                t += 1

        except Exception as e:
            config.logging.error('actuaEventos: Unexpected Error! - {0}'.format(e))
            time.sleep(1)
            try:
                config.lock.release()
            except:
                config.logging.info('actuaEventos: Lock already released')



