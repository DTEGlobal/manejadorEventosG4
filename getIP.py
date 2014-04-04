__author__ = 'Cesar'

#-------------------------------------------------------------------------------
# Name:        main
# Purpose:
#
# Author:      Cesar
#
# Created:     02/21/2014
# Copyright:   (c) Petrolog 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import os
import re
import time
import config


def waitForIP():
    global localaddress
    IpMatch = None
    while IpMatch is None:
        time.sleep(1)
        config.logging.info("Trying to get IP")
        # Find LocalIp from OS.
        ifconfig = os.popen("ifconfig").read()
        # Match LocalIp with Regular Expression
        IpMatch = re.search('192.\d{1,3}\.\d{1,3}.\d{1,3}', ifconfig)
    # Assign Result
    localaddress = IpMatch.group()
    config.logging.info("Local IP:{0}".format(localaddress))
