"""
Panel which displays donators and enables editing of them.
"""

import ceGUI

import Common
import Models

class Panel(Common.BasePanel):

    def OnCreateFilterArgs(self):
        ceGUI.FilterArgStr(self, "surname", "Surname:", size = (150, -1))
        ceGUI.FilterArgStr(self, "givenNames", "Given Names:",
                size = (150, -1))


class Grid(Common.BaseGrid):

    def OnCreate(self):
        super(Grid, self).OnCreate()
        self.AddColumn("surname", "Surname", defaultWidth = 200)
        self.AddColumn("givenNames", "Given Names", defaultWidth = 200)
        self.AddColumn("assignedNumber", "Number", cls = ceGUI.ColumnInt)
        self.AddColumn("addressLine1", "Address Line 1", defaultWidth = 200)
        self.AddColumn("addressLine2", "Address Line 2", defaultWidth = 200)
        self.AddColumn("addressLine3", "Address Line 3", defaultWidth = 200)

    def OnInsertRow(self, row, choice):
        row.year = self.config.year


class DataSet(ceGUI.DataSet):
    rowClass = Models.Donators
    pkSequenceName = "DonatorId_s"
    pkIsGenerated = True

    def _GetRows(self, surname, givenNames):
        rows = [r for r in self.config.GetCachedRows(self.rowClass) \
                if r.year == self.config.year]
        if surname is not None:
            rows = [r for r in rows if surname in r.surname.upper()]
        if givenNames is not None:
            rows = [r for r in rows if r.givenNames is not None \
                    and givenNames in r.givenNames.upper()]
        return rows

