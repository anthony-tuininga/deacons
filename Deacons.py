"""
Main module for Deacons application.
"""

import ceGUI
import os

import Cache
import Database

class Deacons(ceGUI.Application):
    description = "Deacons"
    copyrightOwner = "Anthony Tuininga"
    copyrightStartYear = 1998
    copyrightEndYear = 2009


class Config(object):
    baseDsn = 'Driver=PostgreSQL;Servername=localhost;Database=deacons;' \
            'readonly=0'

    def __init__(self, app):
        dsn = "%s;uid=%s" % (self.baseDsn, os.environ["LOGNAME"])
        self.connection = Database.Connection(dsn)
        self.cache = Cache.Cache(self.connection)

app = Deacons()
app.MainLoop()

