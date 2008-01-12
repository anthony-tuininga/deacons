"""
Wrapper for ceODBC in order to manage Unicode input as the PostgreSQL
ODBC driver does not handle it yet.
"""

import ceODBC

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

