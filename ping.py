__author__ = 'Emmy'

#-------------------------------------------------------------------------------
# Name:        ping
# Purpose:
#
# Author:      Emmanuel
#
# Created:     06/05/2014
# Copyright:   (c) Petrolog 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import config
import time
import os
import re


def ping():
    pingMatch = None
    while pingMatch is None:
        time.sleep(10)
        config.logging.info("Trying to ping default gateway")
        pingResult = os.popen("ping -c 1 192.168.1.254").read()
        pingMatch = re.search(', 1 received', pingResult)