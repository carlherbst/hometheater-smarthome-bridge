#!/usr/bin/python
""" alexa_tv.py - https://github.com/efpe/

    The idea and some part of the code came from https://github.com/toddmedema/echo
    This will register itself to Alexa as 'tv'.

    You can use "Alexa, turn on TV" or "Alexa turn off TV".

    For the ON event it sends a magic packet to the specified MAC address
    For the OFF event it calls the NodeJS script which calls the WebOS API and turns of the TV.

"""

import fauxmo
import logging
import time
import os
from wakeonlan import wol

from debounce_handler import debounce_handler

logging.basicConfig(level=logging.DEBUG)
# Device name
deviceName = 'tv'

class device_handler(debounce_handler):
    """Publishes the on/off state requested,
       and the IP address of the Echo making the request.
    """
    TRIGGERS = {deviceName: 52000}

    def act(self, client_address, state):
        print "State", state, "from client @", client_address
        if state == True:
            os.system("python lgtv.py on")
            print "Magic packet sent to turn on TV!"
        if state == False:
            os.system("python lgtv.py off")
            print "TV turned off!"
            print os.getegid()
        return True

if __name__ == "__main__":
    # Startup the fauxmo server
    fauxmo.DEBUG = True
    p = fauxmo.poller()
    u = fauxmo.upnp_broadcast_responder()
    u.init_socket()
    p.add(u)

    d = device_handler()
    for trig, port in d.TRIGGERS.items():
        fauxmo.fauxmo(trig, u, p, None, port, d)

    # Loop and poll for incoming Echo requests
    logging.debug("Entering fauxmo polling loop")
    while True:
        try:
            # Allow time for a ctrl-c to stop the process
            p.poll(100)
            time.sleep(0.1)
        except Exception, e:
            logging.critical("Critical exception: " + str(e))
            break
