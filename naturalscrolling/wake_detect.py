#!/usr/bin/python

import time
import dbus      # for dbus communication (obviously)
import gobject   # main loop
from dbus.mainloop.glib import DBusGMainLoop # integration into the main loop
from logging import getLogger

LOGGER = getLogger()

class WakeDetector(object):
    _callback = None
    loop = None

    def start(self, callback):
        LOGGER.debug("gobject mainloop start")
        self._callback = callback

        DBusGMainLoop(set_as_default=True) # integrate into main loob
        bus = dbus.SystemBus()             # connect to dbus system wide
        bus.add_signal_receiver(           # defince the signal to listen to
            self.handle_resume_callback,                      # name of callback function
            'Resuming',                    # singal name
            'org.freedesktop.UPower',      # interface
            'org.freedesktop.UPower'       # bus name
            )

        self.loop = gobject.MainLoop()          # define mainloop
        self.loop.run()

    def handle_resume_callback(self):
        LOGGER.debug("System just resumed from hibernate or suspend")
        if self._callback:
            self._callback()
    
    def stop(self):
        LOGGER.debug("Attempting to quit...")
        if self.loop:
            self._callback = None
            self.loop.quit()
