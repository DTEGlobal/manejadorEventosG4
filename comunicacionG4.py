__author__ = 'Cesar'


import config
import getIP
import serial
import time
import actuaEventos
import mosquitto

port = serial.Serial("/dev/ttyAMA0", baudrate=19200, timeout=1)

tiempoEsc = ""

# Create Mosquitto Client for Watchdog broker
mqttcWC = mosquitto.Mosquitto("serialWC")


def on_connect_cG4WC(mosq, obj, rc):
    config.logging.info("comunicacionG4: Serial Watchdog Client connected")
    mqttcWC.subscribe("#", 0)


def getTiempoEsc():
    global tiempoEsc

    a = tiempoEsc[-2:]
    tiempoEsc = tiempoEsc[:-2]
    tiempoEsc = "{0}20{1}".format(tiempoEsc, a)

    temp = time.strptime(tiempoEsc, '%H:%M:%S %d/%m/%Y')
    return temp


def accionCMD():
    return '01{0}\x0D'.format(actuaEventos.comando)


def SendCommand(cmd_cfg):
    global port, tiempoEsc

    port.flushOutput()
    command = cmd_cfg
    Rx = True
    data_toPrint = command[:-1]
    config.logging.debug("comunicacionG4: TxST: Tx Data->[{}]".format(data_toPrint))
    port.write(command)

    while Rx:
        try:
            MessageFromSerial = port.readline()
            # Remove last 3 chars (CR LF)
            data_toPrint = MessageFromSerial[:-2]
            if data_toPrint[2] == "H":
                tiempoEsc = data_toPrint[3:]
            config.logging.debug("comunicacionG4: RxST: Rx Data->[{}]".format(data_toPrint))
            Rx = False

        except serial.SerialException as e:
            config.logging.error("comunicacionG4: Error - {0}".format(e))
            Rx = False
        except IndexError as i:
            config.logging.error("comunicacionG4: Error - {0}".format(i))
            Rx = False


def serialDaemon():
    config.logging.info("comunicacionG4: SendCommand Thread Running ...")
    # Connect to mqtt watchdog server
    mqttcWC.on_connect = on_connect_cG4WC
    mqttcWC.connect(getIP.localaddress, 1884)

    while True:
        SendCommand(accionCMD())
        SendCommand("01H\x0D")

        t = 0
        while t < config.delaySerial:
            time.sleep(1)
            # mqtt client loop for watchdog keep alive
            config.logging.debug("verificaRelojSistema: Watchdog Keep Alive")
            mqttcWC.loop()
            t += 1