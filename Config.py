"""
Configuration for Deacons application.
"""

import ceGUI
import ceODBC
import os

import Cache

class Config(ceGUI.Config):
    baseDsn = 'Driver=PostgreSQL;Servername=%s;Database=deacons;readonly=0'

    def __init__(self, app):
        super(Config, self).__init__(app)
        server = os.environ.get("DEACONS_DB_SERVER", "localhost")
        baseDsn = self.baseDsn % server
        dsn = "%s;uid=%s" % (baseDsn, os.environ["LOGNAME"])
        self.connection = Connection(dsn)
        self.cache = app.cache = Cache.Cache(self.connection)
        app.copyAttributes.append("cache")


class Connection(ceODBC.Connection):

    def cursor(self):
        return Cursor(self)


class Cursor(ceODBC.Cursor):

    def execute(self, statement, *args):
        actualArgs = []
        if len(args) == 1 and isinstance(args[0], (list, tuple)):
            args = args[0]
        for arg in args:
            if isinstance(arg, unicode):
                arg = arg.encode("utf-8")
            actualArgs.append(arg)
        super(Cursor, self).execute(statement, *actualArgs)

