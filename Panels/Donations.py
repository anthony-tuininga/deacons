"""
Panel which displays donations and enables editing of them.
"""

import ceGUI

import Common
import Models

class Panel(Common.BasePanel):

    def __SetCauseChoices(self, rows):
        causeIdDict = dict.fromkeys(r.causeId for r in rows)
        causes = [c for c in self.config.GetCachedRows(Models.Causes) \
                if c.causeId in causeIdDict]
        causes.sort(key = lambda x: x.description.upper())
        choices = [(c.causeId, c.description) for c in causes]
        choices.insert(0, (None, "(Any)"))
        self.causeFilterArg.SetChoices(choices)

    def __SetDateCollectedChoices(self, rows):
        datesCollected = list(dict.fromkeys(r.dateCollected for r in rows))
        datesCollected.sort()
        choices = [(d, d.strftime("%Y/%m/%d")) for d in datesCollected]
        choices.insert(0, (None, "(Any)"))
        self.dateCollectedFilterArg.SetChoices(choices)

    def __SetDateDepositedChoices(self, rows):
        datesDeposited = list(dict.fromkeys(r.dateDeposited for r in rows))
        datesDeposited.sort()
        choices = [(d, d.strftime("%Y/%m/%d")) for d in datesDeposited]
        choices.insert(0, (None, "(Any)"))
        self.dateDepositedFilterArg.SetChoices(choices)

    def GetBaseRows(self):
        return self.grid.dataSet.rowClass.GetRows(self.config.dataSource,
                year = self.config.year)

    def OnCreateFilterArgs(self):
        self.dateDepositedFilterArg = ceGUI.FilterArgChoiceMultiple(self,
                "dateDeposited", "Date Deposited:", size = (125, -1))
        self.dateCollectedFilterArg = ceGUI.FilterArgChoiceMultiple(self,
                "dateCollected", "Date Collected:", size = (125, -1))
        self.causeFilterArg = ceGUI.FilterArgChoiceMultiple(self, "causeId",
                "Cause:", size = (300, -1))

    def OnPopulateBaseRows(self, rows):
        self.__SetDateDepositedChoices(rows)
        self.__SetDateCollectedChoices(rows)
        self.__SetCauseChoices(rows)


class Grid(Common.BaseGrid):

    def OnCreate(self):
        self.AddColumn("dateDeposited", "Deposited", defaultWidth = 100,
                cls = ceGUI.ColumnDate)
        self.AddColumn("dateCollected", "Collected", defaultWidth = 100,
                cls = ceGUI.ColumnDate)
        self.AddColumn("cash", "Cash", defaultWidth = 100,
                cls = ceGUI.ColumnBool)
        self.AddColumn("causeId", "Cause", defaultWidth = 200,
                cls = Common.ColumnCauseDescription)
        self.AddColumn("donatorId", "Donator", defaultWidth = 300,
                cls = Common.ColumnDonatorName)
        self.AddColumn("amount", "Amount", defaultWidth = 200,
                cls = ceGUI.ColumnMoney)


class DataSet(ceGUI.DataSet):
    rowClass = Models.Donations

    def _GetRows(self, rows, datesDeposited, datesCollected, causeIds):
        if datesDeposited:
            rows = [r for r in rows if r.dateDeposited in datesDeposited]
        if datesCollected:
            rows = [r for r in rows if r.dateCollected in datesCollected]
        if causeIds:
            rows = [r for r in rows if r.causeId in causeIds]
        return rows

