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

import os
import re
from logging import getLogger

LOGGER = getLogger()

class XinputWarper(object):
    # Singleton
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            LOGGER.debug("New instance")
            cls._instance = super(XinputWarper, cls).__new__(cls, *args,
                                                                 **kwargs)
            cls._instance.__xinput_list_pattern = re.compile(
                r'\s+([A-z0-9\s\-\(\)\/]+)\s+id=(\d+)\s+\[slave\s+pointer.*\]')
            cls._instance.__xinput_list = None
        return cls._instance

    def get_xinput_list(self):
        return self.__xinput_list
    xinput_list = property(get_xinput_list)

    def enable_natural_scrolling(self, device_xid, enabled):
        """
        Global method to apply or not Natural Scrolling
        """
        map = os.popen("xinput get-button-map \"%s\"" %
                       device_xid).read().strip()
        
        LOGGER.debug("Setting scrolling reverse to %s" % enabled)
        LOGGER.debug("Current map: %s" % map)

        if enabled == True:
            map = map.replace("4 5", "5 4")
            map = map.replace("6 7", "7 6")
        else:
            map = map.replace("5 4", "4 5")
            map = map.replace("7 6", "6 7")

        os.system("xinput set-button-map \"%s\" %s" % (device_xid, map))

    def find_xid_by_name(self, name):
        """
        Extract from the xinput list the id of the given device name
        """
        xinput_list = self._xinput_list(name)
        for device_info in self.__xinput_list_pattern.findall(xinput_list):
            if device_info[0].strip() == name:
                return device_info[1]
        return None

    def first_xid(self):
        """
        Extract from the xinput list the id of the first detected device
        """
        xinput_list = self._xinput_list()
        return self.__xinput_list_pattern.findall(xinput_list)[0][1]

    def reset_cache(self):
        """
        Clear xinput cache in order to force refresh
        """
        LOGGER.debug("Reset cache")
        self.__xinput_list = None
    
    def read_xinputs(self):
        return self._xinput_list()

    def _xinput_list(self, name=None):
        """
        Refresh cache and/or search in cached xinput list
        """
        if not self.__xinput_list:
            LOGGER.debug("Requesting xinouts:")
            self.__xinput_list = os.popen(("xinput list | grep -v 'XTEST' "
                                           "| grep -v '\[master '")).read()
            LOGGER.debug(self.__xinput_list)

        if name:
            res = re.search(r'(.*%s.*)' % re.escape(name), self.__xinput_list)
            if res:
                return res.group(1)
        return self.__xinput_list
