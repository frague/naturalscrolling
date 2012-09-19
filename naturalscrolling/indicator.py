### BEGIN LICENSE
# Copyright (C) 2011 Guillaume Hain <zedtux@zedroot.org>
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 3, as published
# by the Free Software Foundation
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>
### END LICENSE

import gtk
import appindicator
import time

from naturalscrolling_lib import naturalscrollingconfig
from naturalscrolling_lib.gconfsettings import GConfSettings
from naturalscrolling_lib.udevobservator import UDevObservator
from naturalscrolling.indicatormenu import IndicatorMenu
from naturalscrolling.xinputwarper import XinputWarper
from wake_detect import WakeDetector
from logging import getLogger

LOGGER = getLogger()

class Indicator(object):
    # Singleton
    _instance = None
    _init_done = False
    watchman = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Indicator, cls).__new__(cls, *args,
                                                          **kwargs)
        return cls._instance

    def __init__(self):
        LOGGER.debug("Indicator initialization")

        # Initialize a new AppIndicator
        self.indicator = appindicator.Indicator(
            "natural-scrolling-indicator",
            "natural-scrolling-status-not-activated",
            appindicator.CATEGORY_APPLICATION_STATUS)
        media_path = "%s/media/" % naturalscrollingconfig.get_data_path()
        self.indicator.set_icon_theme_path(media_path)
        self.indicator.set_attention_icon(
            "natural-scrolling-status-activated")

        self.menu = IndicatorMenu()
        self.menu.indicator = self
        self.indicator.set_menu(self.menu)

        # Initialize the UDev client
        udev_observator = UDevObservator()
        udev_observator.on_update_execute(self.menu.refresh)
        udev_observator.start()

        # Force the first refresh of the menu in order to populate it.
        self.menu.refresh(udev_observator.gather_devices())

        # When something change in GConf, push it to the Indicator menu
        # in order to update the status of the device as checked or unchecked
        GConfSettings().server().on_update_fire(self.menu.update_check_menu_item)

        # Initialize GConf in order to be up-to-date with existing devices
        GConfSettings().initialize(udev_observator.gather_devices())

    def status_attention(self):
        self.set_status(appindicator.STATUS_ATTENTION)

    def status_active(self):
        self.set_status(appindicator.STATUS_ACTIVE)

    @property
    def isreversed(self):
        return self.menu.enabled

    def check_scrolling(self):
        if self.isreversed:
            self.indicator.set_status(appindicator.STATUS_ATTENTION)
        else:
            self.indicator.set_status(appindicator.STATUS_ACTIVE)
        return True

    def refresh_loop(self):
        if not UDevObservator().gather_devices():
            LOGGER.debug("Refresh loop - FAILED")
            return True
        LOGGER.debug("Refresh loop - SUCCESS")

        bool_int = 1 if self.isreversed else 0
        LOGGER.debug("Reverting once to %s" % (1 - bool_int))
        self.menu.set_scrolling_state(1 - bool_int)
        time.sleep(1)
        LOGGER.debug("Reverting twice to %s" % bool_int)
        self.menu.set_scrolling_state(bool_int)
        return False

    def refresh(self):
        LOGGER.debug("Refresh loop initiated...")
        if self.refresh_loop():
            gtk.timeout_add(10 * 1000, self.refresh_loop)

    def start(self):
        self.check_scrolling()
        self.menu.watchman = WakeDetector()
        self.menu.watchman.start(self.refresh)
        try:
            gtk.main()
        except KeyboardInterrupt:
            pass
