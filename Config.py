"""
Configuration for Deacons application.
"""

import ceODBC
import os

import Cache

class Config(object):
    baseDsn = 'Driver=PostgreSQL;Servername=localhost;Database=deacons;' \
            'readonly=0'

    def __init__(self, app):
        dsn = "%s;uid=%s" % (self.baseDsn, os.environ["LOGNAME"])
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
