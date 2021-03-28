"""
Frame for editing cheque donations.
"""

import ceGUI
import wx

from . import BaseDonations

import Common
import Models

class Frame(BaseDonations.Frame):
    hasToolbar = hasMenus = False
    defaultSize = (650, 700)
    title = "Edit Cheque Donations"

class TopPanel(BaseDonations.TopPanel):
    pass


class BottomPanel(BaseDonations.BottomPanel):

    def GetRetrievalArgs(self):
        return [self.tray.trayId, False]


class Grid(BaseDonations.Grid):
    customCellAttributes = True

    def _CreateContextMenu(self):
        super(Grid, self)._CreateContextMenu()
        self.menu.AddSeparator()
        self.editSplitChequeMenuItem = self.menu.AddEntry(self,
                "Edit Split Cheque...\tCtrl-T", method=self.OnEditSplitCheque,
                passEvent=False)

    def _GetAccelerators(self):
        accelerators = super(Grid, self)._GetAccelerators()
        accelerators.append((wx.ACCEL_CTRL, ord('T'),
                self.editSplitChequeMenuItem.GetId()))
        return accelerators

    def _RowIsEmpty(self, row):
        return row.donatorId is None and row.causeId is None and \
                row.amount == 0

    def OnContextMenu(self):
        selectedItems = self.GetSelectedItems()
        canEditSubItem = len(selectedItems) == 1 \
                and selectedItems[0].donationId is not None
        self.editSplitChequeMenuItem.Enable(canEditSubItem)
        super(Grid, self).OnContextMenu()

    def OnCreate(self):
        super(Grid, self).OnCreate()
        self.AddColumn("donatorId", "Donator", defaultWidth = 300,
                cls = Common.ColumnDonatorName, required = True)
        self.AddColumn("causeId", "Cause", defaultWidth = 200,
                cls = ColumnCauseDescription, required = True)
        self.AddColumn("amount", "Amount", defaultWidth = 200,
                cls = ceGUI.ColumnMoney, required = True)

    def OnEditSplitCheque(self):
        dialogName = "EditDialogs.SplitChequeDonation.Frame"
        frame = self.GetParent().OpenWindow(dialogName)
        frame.Show()

    def OnGetCustomCellAttributes(self, row, column, attr):
        if row.splitComponents:
            attr.SetReadOnly()


class ColumnCauseDescription(Common.ColumnCauseDescription):
    splitDescription = "-- Split --"

    def GetNativeValue(self, row):
        if row.splitComponents:
            return self.splitDescription
        return super(ColumnCauseDescription, self).GetNativeValue(row)


class DataSet(BaseDonations.DataSet):
    rowClass = Models.Donations
    retrievalAttrNames = "trayId cash"

    def _GetRows(self, *args):
        baseRows = super(DataSet, self)._GetRows(*args)
        rows = []
        rowDict = {}
        for row in baseRows:
            splitRow = rowDict.get(row.donationId)
            if splitRow is None:
                rowDict[row.donationId] = row
                rows.append(row)
            else:
                if splitRow.splitComponents is None:
                    splitRow.splitComponents = [splitRow.Copy()]
                splitRow.splitComponents.append(row)
                splitRow.amount += row.amount
        return rows

    def InsertRowInDatabase(self, transaction, row):
        if not row.splitComponents:
            super(DataSet, self).InsertRowInDatabase(transaction, row)

    def UpdateRowInDatabase(self, transaction, row, origRow):
        if not row.splitComponents:
            super(DataSet, self).UpdateRowInDatabase(transaction, row, origRow)
