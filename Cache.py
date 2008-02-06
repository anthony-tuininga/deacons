"""
Define cache for commonly used items.
"""

import ceDatabase

class Cache(object):

    def __init__(self, connection):
        self.connection = connection
        self.Clear()

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
        self.causesById = dict((c.causeId, c) for c in self.causes)

    def __PopulateDonators(self, cursor):
        cursor.execute("""
                select
                  DonatorId,
                  IsActive,
                  LastName,
                  GivenNames,
                  Address
                from Donators""")
        cursor.rowfactory = Donator
        self.donators = cursor.fetchall()
        self.donatorsById = dict((d.donatorId, d) for d in self.donators)
        for donator in self.donators:
            if donator.givenNames is None:
                donator.name = donator.lastName
            else:
                donator.name = "%s %s" % \
                        (donator.givenNames, donator.lastName)

    def CauseForId(self, causeId):
        return self.causesById[causeId]

    def Causes(self):
        return self.causes

    def Clear(self):
        cursor = self.connection.cursor()
        self.__PopulateCauses(cursor)
        self.__PopulateDonators(cursor)

    def DonatorForId(self, donatorId):
        return self.donatorsById[donatorId]

    def Donators(self):
        return self.donators


class Cause(ceDatabase.Row):
    attrNames = "causeId description reported active address"
    charBooleanAttrNames = "reported active"


class Donator(ceDatabase.Row):
    attrNames = "donatorId active lastName givenNames addresss"
    charBooleanAttrNames = "active"
    extraAttrNames = "name"

