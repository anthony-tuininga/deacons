"""
Define cache for commonly used items.
"""

import ceDatabase
import ceDatabaseCache

class Cache(ceDatabaseCache.Cache):

    class CausesSubCache(ceDatabaseCache.SubCache):
        allRowsMethodCacheAttrName = "Causes"
        loadAllRowsOnFirstLoad = True
        cacheAttrName = "causes"

        class rowClass(ceDatabase.Row):
            tableName = "Causes"
            attrNames = "causeId description isReported isActive address"
            charBooleanAttrNames = "isReported isActive"
            extraAttrNames = sortByAttrNames = "searchDescription"
            pkAttrNames = "causeId"
            reprName = "Cause"

        class Id(ceDatabaseCache.SingleRowPath):
            retrievalAttrNames = "causeId"
            cacheAttrName = "CauseForId"

        def SetExtraAttrValues(self, cache, row):
            row.searchDescription = row.description.upper()

    class DonatorsSubCache(ceDatabaseCache.SubCache):
        allRowsMethodCacheAttrName = "Donators"
        loadAllRowsOnFirstLoad = True
        cacheAttrName = "donators"

        class rowClass(ceDatabase.Row):
            tableName = "Donators"
            attrNames = "donatorId isActive lastName givenNames address"
            charBooleanAttrNames = "isActive"
            extraAttrNames = "name reversedName searchName searchReversedName"
            pkAttrNames = "donatorId"
            reprName = "Donator"

        class Id(ceDatabaseCache.SingleRowPath):
            retrievalAttrNames = "donatorId"
            cacheAttrName = "DonatorForId"

        def SetExtraAttrValues(self, cache, row):
            if row.givenNames is None:
                row.name = row.reversedName = row.lastName
            else:
                row.name = "%s %s" % (row.givenNames, row.lastName)
                row.reversedName = "%s, %s" % (row.lastName, row.givenNames)
            row.searchName = row.name.upper()
            row.searchReversedName = row.reversedName.upper()

    class DonatorsForYearSubCache(ceDatabaseCache.SubCache):
        loadAllRowsOnFirstLoad = True
        cacheAttrName = "donatorsForYear"

        class rowClass(ceDatabase.Row):
            tableName = "DonatorsForYear"
            attrNames = "donatorId year assignedNumber"
            pkAttrNames = "year donatorId"
            reprName = "DonatorForYear"

        class Donator(ceDatabaseCache.SingleRowPath):
            retrievalAttrNames = "donatorId year"
            cacheAttrName = "_AssignedNumberForDonator"
            ignoreRowNotCached = True

        class AssignedNumber(ceDatabaseCache.SingleRowPath):
            retrievalAttrNames = "year assignedNumber"
            cacheAttrName = "_DonatorForAssignedNumber"
            ignoreRowNotCached = True

        class Year(ceDatabaseCache.MultipleRowPath):
            retrievalAttrNames = "year"
            cacheAttrName = "DonatorsForYear"

    def AssignedNumberForDonator(self, donator, year):
        row = self._AssignedNumberForDonator(donator.donatorId, year)
        if row is not None:
            return row.assignedNumber

    def DonatorForAssignedNumber(self, year, assignedNumber):
        row = self._DonatorForAssignedNumber(year, assignedNumber)
        if row is not None:
            return self.DonatorForId(row.donatorId)

