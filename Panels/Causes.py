"""
Panel which displays causes and enables editing of them.
"""

import ceGUI

import Common
import Models

class Panel(Common.BasePanel):
    pass


class Grid(Common.BaseGrid):

    def OnCreate(self):
        self.AddColumn("description", "Description", defaultWidth = 200)
        self.AddColumn("deductible", "Deductible", cls = ceGUI.ColumnBool)
        self.AddColumn("reported", "Reported", cls = ceGUI.ColumnBool)
        self.AddColumn("donationAccountCode", "Donation Account",
                defaultWidth = 150)
        self.AddColumn("looseCashAccountCode", "Loose Cash Account",
                defaultWidth = 150)
        self.AddColumn("notes", "Notes", defaultWidth = 200)

    def OnInsertRow(self, row, choice):
        row.year = self.config.year
        row.deductible = True
        row.reported = True


class DataSet(ceGUI.DataSet):
    rowClass = Models.Causes
    pkSequenceName = "CauseId_s"
    pkIsGenerated = True

    def _GetRows(self):
        return [r for r in self.config.GetCachedRows(self.rowClass) \
                if r.year == self.config.year]

