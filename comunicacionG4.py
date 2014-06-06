__author__ = 'Cesar'


import config
import serial
import time
import actuaEventos
import mosquitto
import MySQLdb
import bitState
import re
import ping

port = serial.Serial("/dev/ttyAMA0", baudrate=19200, timeout=1)

tiempoEsc = ""
servingConsole = False
updateTime = ""

# Create Mosquitto Client for Watchdog broker
mqttcWC = mosquitto.Mosquitto("serialWC")


def on_connect_cG4WC(mosq, obj, rc):
    config.logging.info("comunicacionG4: Serial Watchdog Client connected")
    mqttcWC.subscribe("#", 0)


def tiempoEscValido():
    """
    Returns True if the time acquired by H command has a valid date:
    HH:MM:SS dd:mm:yy
    with no hex numbers. False otherwise
    """
    if re.search('\d{2}:\d{2}:\d{2} \d{2}/\d{2}/\d{2}', tiempoEsc):
        return True
    else:
        return False


def tiempoEscDisponible():
    """
    Returns True if the time has been acquired by H command. False otherwise
    """
    if tiempoEsc == "":
        return False
    else:
        return True


def getTiempoEsc():
    """
    Returns the time acquired by H command. Do not use without first making sure the time is available
    by using tiempoEscDisponible.
    """
    global tiempoEsc

    if tiempoEscDisponible():
        return time.strptime(tiempoEsc, '%H:%M:%S %d/%m/%y')
    else:
        # Return invalid time (Time is less than 01/01/2000) see main.py
        return time.localtime(0)


def setTiempoEsc():
    global updateTime

    updateTime = time.strftime('%H:%M:%S %d/%m/%y ', time.localtime())


def updateEstado(cmd_e):
    estado = bitState.getBitState(cmd_e[18:20], 7)
    config.logging.info("comunicacionG4: Estado: {0}".format(estado))

    # Construct DB object
    db = MySQLdb.connect(host='localhost', user='root', passwd='petrolog', db='eventosg4')
    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    # TODO Code for more than one device (hardcoded to 01)
    dirDispositivo = '01'
    # Update estado in dispositivo
    cursor.execute("UPDATE dispositivo SET estado = \'{0}\' "
                   'WHERE dirDispositivo = \'{1}\''.format(estado, dirDispositivo))
    db.commit()
    # Close DB object
    cursor.close()
    db.close()

    resposeToConsole(cmd_e)


def resposeToConsole(rx):
    config.logging.info("comunicacionG4: respuestaConsola: Rx Data->[{}]".format(rx))

    # Construct DB object
    db = MySQLdb.connect(host='localhost', user='root', passwd='petrolog', db='eventosg4')
    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    # TODO Code for more than one device (hardcoded to 01)
    dirDispositivo = '01'
    # Set response
    cursor.execute('UPDATE dispositivo SET respuestaConsola = \'{0}\' '
                   'WHERE dirDispositivo = \'{1}\''.format(rx, dirDispositivo))
    # Clear command
    cursor.execute('UPDATE dispositivo SET comandoConsola = \'\' '
                   'WHERE dirDispositivo = \'{0}\''.format(dirDispositivo))
    db.commit()
    # Close DB object
    cursor.close()
    db.close()


def SendCommand(cmd_cfg):
    global port, tiempoEsc, servingConsole

    port.flushOutput()
    command = cmd_cfg
    Rx = True
    data_toPrint = command[:-1]
    config.logging.debug("comunicacionG4: Tx Data->[{}]".format(data_toPrint))
    port.write(command)

    while Rx:
        try:
            MessageFromSerial = port.readline()
            # Remove last 3 chars (CR LF)
            data_toPrint = MessageFromSerial[:-2]
            if servingConsole:
                if data_toPrint[2] == "E":
                    updateEstado(data_toPrint)
                else:
                    resposeToConsole(data_toPrint)
                servingConsole = False
            elif data_toPrint[2] == "H":
                tiempoEsc = data_toPrint[3:]
                config.logging.debug("comunicacionG4: Reloj ESC -> [{}]".format(data_toPrint))
            elif data_toPrint[2] == "S":
                config.logging.info("comunicacionG4: Nuevo Reloj ESC -> [{}]".format(data_toPrint))

            else:
                config.logging.debug("comunicacionG4: Rx Data- > [{}]".format(data_toPrint))
            Rx = False

        except serial.SerialException as e:
            config.logging.error("comunicacionG4: Error - {0}".format(e))
            if servingConsole:
                servingConsole = False
                resposeToConsole('   Error - {0}'.format(e))
            Rx = False
        except IndexError as i:
            config.logging.error("comunicacionG4: Error - {0}".format(i))
            if servingConsole:
                servingConsole = False
                resposeToConsole('   Error - {0}'.format(i))
            Rx = False


def serialDaemon():
    global servingConsole, updateTime

    config.logging.info("comunicacionG4: SendCommand Thread Running ...")
    # Connect to mqtt watchdog server
    mqttcWC.on_connect = on_connect_cG4WC
    mqttcWC.connect('localhost', 1884)

    while True:
        try:
            # Construct DB object
            db = MySQLdb.connect(host='localhost', user='root', passwd='petrolog', db='eventosg4')
            cursor = db.cursor(MySQLdb.cursors.DictCursor)
            # TODO Code for more than one device (hardcoded to 01)
            cursor.execute('SELECT comandoConsola FROM dispositivo')
            comandoConsola = cursor.fetchall()
            if comandoConsola[0]['comandoConsola'] != '':
                servingConsole = True
                config.logging.info("comunicacionG4: Comando Consola = {0}".format(comandoConsola[0]['comandoConsola']))
                SendCommand('01{0}\x0D'.format(comandoConsola[0]['comandoConsola']))
            elif updateTime != '':
                config.logging.info("comunicacionG4: Corrigiendo Reloj ESC")
                SendCommand('01SH{0}\x0D'.format(updateTime))
                updateTime = ''
            elif ping.raspberrypiKiller == 1:
                config.logging.critical("comunicacionG4: wireless adapter not detected... powering off")
                SendCommand('A60')
            else:
                SendCommand('01{0}\x0D'.format(actuaEventos.comando))
            SendCommand('01H\x0D')

            # Close DB object
            cursor.close()
            db.close()

            t = 0
            while t < config.delaySerial:
                # mqtt client loop for watchdog keep alive
                config.logging.debug("comunicacionG4: Watchdog Keep Alive")
                mqttcWC.loop(0)
                time.sleep(1)
                t += 1
        except Exception as e:
            config.logging.error('comunicacionG4: Unexpected Error! - {0}'.format(e.args))
            time.sleep(1)
