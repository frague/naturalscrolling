# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
### BEGIN LICENSE
# Copyright (C) 2011 Eumorphed UG,
# Charalampos Emmanouilidis <ce@eumorphed.com>
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 3, as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>
### END LICENSE

import sys
import time
import optparse
import gettext
gettext.install("naturalscrolling")
from logger import make_custom_logger

from naturalscrolling_lib.naturalscrollingconfig import *
from naturalscrolling.indicator import Indicator
from naturalscrolling_lib.gconfsettings import GConfSettings
from naturalscrolling.xinputwarper import XinputWarper
from naturalscrolling_lib.debugger import Debugger

LOGGER = make_custom_logger()

def main():
    """Support for command line options"""
    parser = optparse.OptionParser(version="%%prog %s" % appliation_version())
    parser.add_option("-v", "--verbose", action="count", dest="verbose",
        help=_("Show debug messages (-vv debugs naturalscrolling_lib also)"))
    parser.add_option("-d", "--debug", action="store_true",
        help=_("Enable debuging"))
    parser.add_option("-r", "--restart", action="store_true",
        help=_("Switch service off and on again"))
    (options, args) = parser.parse_args()

    if options.debug:
        Debugger().execute()
        sys.exit(0)

    if options.restart:
        LOGGER.debug("Refreshing state from console ...")
        try:
            Indicator().refresh()
        except Exception:
            LOGGER.error("Unable to restart this time")
            sys.exit(1)
        sys.exit(0)

    # Initialize the GConf client
    GConfSettings().server().on_update_fire(
        XinputWarper().enable_natural_scrolling)

    Indicator().start()
