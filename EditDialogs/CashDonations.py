"""
Frame for editing cash donations.
"""

import ceGUI

from . import BaseDonations

import Common
import Models

class Frame(BaseDonations.Frame):
    hasToolbar = hasMenus = False
    defaultSize = (650, 700)
    title = "Edit Cash Donations"

    def OnCreate(self):
        parent = self.GetParent()
        self.tray, = parent.grid.GetSelectedItems()
        self.panel = Panel(self)
        super(Frame, self).OnCreate()
        self.panel.grid.SetFocus()


class Panel(BaseDonations.Panel):

    def OnCreate(self):
        parent = self.GetParent()
        self.tray = parent.tray
        super(Panel, self).OnCreate()

    def GetRetrievalArgs(self):
        return [self.tray.trayId, True]

    def Retrieve(self, refresh):
        super(Panel, self).Retrieve(refresh)
        if self.grid.GetNumberRows() == 0:
            self.grid.InsertRows(0)


class Grid(BaseDonations.Grid):
    sortOnRetrieve = False

    def _RowIsEmpty(self, row):
        return row.donatorId is None and row.amount == 0

    def OnInsertRow(self, row, choice):
        row.causeId = self.tray.causeId
        row.cash = True
        row.amount = 0

    def DeleteRows(self, row, numRows = 1):
        super(Grid, self).DeleteRows(row, numRows)
        self.Update()

    def OnCreate(self):
        parent = self.GetParent()
        self.tray = parent.tray
        self.AddColumn("donatorId", "Donator", defaultWidth = 300,
                cls = Common.ColumnDonatorName, required = True)
        self.AddColumn("amount", "Amount", defaultWidth = 200,
                cls = ceGUI.ColumnMoney, required = True)
        super(Grid, self).OnCreate()


class DataSet(BaseDonations.DataSet):
    rowClass = Models.Donations
    retrievalAttrNames = "trayId cash"

