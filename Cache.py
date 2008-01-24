"""
Define cache for commonly used items.
"""

import ceDatabase

class Cache(object):

    def __init__(self, connection):
        self.connection = connection
        self.causes = []
        self.causesById = {}
        cursor = self.connection.cursor()
        self.__PopulateCauses(cursor)

    def __PopulateCauses(self, cursor):
        cursor.execute("""
                select
                  CauseId,
                  Description,
                  IsReported,
                  IsActive,
                  Address
                from Causes""")
        cursor.rowfactory = Cause
        self.causes = cursor.fetchall()
        self.causesById = dict([(c.causeId, c) for c in self.causes])

    def CauseForId(self, causeId):
        return self.causesById[causeId]

    def Causes(self):
        return self.causes


class Cause(ceDatabase.Row):
    attrNames = "causeId description reported active address"

