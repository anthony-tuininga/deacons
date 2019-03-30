"""
Frame for editing cheque donations.
"""

import ceGUI

from . import BaseDonations

import Common
import Models

class Frame(BaseDonations.Frame):
    hasToolbar = hasMenus = False
    defaultSize = (650, 700)
    title = "Edit Cheque Donations"

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
        return [self.tray.trayId, False]

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
        row.cash = False
        row.amount = 0

    def DeleteRows(self, row, numRows = 1):
        super(Grid, self).DeleteRows(row, numRows)
        self.Update()

    def OnCreate(self):
        parent = self.GetParent()
        self.tray = parent.tray
        self.AddColumn("donatorId", "Donator", defaultWidth = 300,
                cls = Common.ColumnDonatorName, required = True)
        self.AddColumn("causeId", "Cause", defaultWidth = 200,
                cls = Common.ColumnCauseDescription, required = True)
        self.AddColumn("amount", "Amount", defaultWidth = 200,
                cls = ceGUI.ColumnMoney, required = True)
        super(Grid, self).OnCreate()


class DataSet(BaseDonations.DataSet):
    rowClass = Models.Donations
    retrievalAttrNames = "trayId cash"

