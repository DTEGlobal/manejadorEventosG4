__author__ = 'Cesar'


import serial
import time
import actuaEventos
import config




port = serial.Serial("/dev/ttyAMA0", baudrate=19200, timeout=1)

tiempoEsc = ""

def getTiempoEsc():
    global tiempoEsc

    tiempoEsc = tiempoEsc[:-2]
    tiempoEsc = tiempoEsc+"2014"

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
    config.logging.debug("[{}]TxST: Tx Data->[{}]".format(time.clock(), data_toPrint))
    port.write(command)

    while Rx:
        try:
            MessageFromSerial = port.readline()
            # Remove last 3 chars (CR LF)
            data_toPrint = MessageFromSerial[:-2]
            if data_toPrint[2] == "H":
                tiempoEsc = data_toPrint[3:]
            config.logging.debug("[{}]RxST: Rx Data->[{}]".format(time.clock(), data_toPrint))
            Rx = False

        except serial.SerialException as e:
            config.logging.error("Error: ...{0}".format(e))
            Rx = False
        except IndexError as i:
            config.logging.error("Error: ...{0}".format(i))
            Rx = False






def serialDaemon():

    config.logging.info("TxST: SendCommand Thread Running ...")
    while True:
        SendCommand(accionCMD())
        SendCommand("01H\x0D")
        time.sleep(config.delaySerial)
