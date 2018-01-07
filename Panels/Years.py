"""
Panel displaying information about years.
"""

import ceGUI

import Common
import Models

class Panel(Common.BasePanel):
    pass


class Grid(Common.BaseGrid):

    def OnCreate(self):
        self.AddColumn("year", "Year", defaultWith = 50)
        self.AddColumn("budgetAmount", "Budget Amount",
                cls = ceGUI.ColumnMoney, defaultWidth = 175)
        self.AddColumn("receiptsIssued", "Receipts Issued",
                cls = ceGUI.ColumnBool, defaultWidth = 200)
        self.AddColumn("notes", "Notes", defaultWidth = 200)


class DataSet(ceGUI.DataSet):
    rowClass = Models.Years

