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
        for cause in self.causes:
            cause.searchDescription = cause.description.upper()

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
                donator.name = donator.reversedName = donator.lastName
            else:
                donator.name = "%s %s" % \
                        (donator.givenNames, donator.lastName)
                donator.reversedName = "%s, %s" % \
                        (donator.lastName, donator.givenNames)
            donator.searchName = donator.name.upper()
            donator.searchReversedName = donator.reversedName.upper()

    def __PopulateDonatorsForYear(self, year):
        if year not in self.assignedNumbersByDonator:
            cursor = self.connection.cursor()
            cursor.execute("""
                    select
                      DonatorId,
                      AssignedNumber
                    from DonatorsForYear
                    where Year = ?""",
                    year)
            rows = [(self.donatorsById[i], n) for i, n in cursor]
            self.assignedNumbersByDonator[year] = dict(rows)
            self.donatorsByAssignedNumber[year] = \
                    dict((n, d) for d, n in rows)

    def AssignedNumberForDonator(self, donator, year):
        self.__PopulateDonatorsForYear(year)
        return self.assignedNumbersByDonator[year].get(donator)

    def CauseForId(self, causeId):
        return self.causesById[causeId]

    def Causes(self, sortItems = True, activeOnly = True):
        if not sortItems:
            if not activeOnly:
                return self.causes
            return [c for c in self.causes if c.active]
        itemsToSort = [(c.description.upper(), c) for c in self.causes \
                if c.active or not activeOnly]
        return [c for d, c in sorted(itemsToSort)]

    def Clear(self):
        cursor = self.connection.cursor()
        self.__PopulateCauses(cursor)
        self.__PopulateDonators(cursor)
        self.assignedNumbersByDonator = {}
        self.donatorsByAssignedNumber = {}

    def DonatorForAssignedNumber(self, year, assignedNumber):
        self.__PopulateDonatorsForYear(year)
        return self.donatorsByAssignedNumber[year].get(assignedNumber)

    def DonatorForId(self, donatorId):
        return self.donatorsById[donatorId]

    def Donators(self):
        return self.donators


class Cause(ceDatabase.Row):
    attrNames = "causeId description reported active address"
    charBooleanAttrNames = "reported active"
    extraAttrNames = "searchDescription"


class Donator(ceDatabase.Row):
    attrNames = "donatorId active lastName givenNames address"
    charBooleanAttrNames = "active"
    extraAttrNames = "name reversedName searchName searchReversedName"

