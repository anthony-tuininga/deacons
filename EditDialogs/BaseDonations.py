"""
Base frame for editing donations. Note that a frame used instead of a dialog
because otherwise some of the key events on the grid are swallowed!
"""

import ceGUI
import wx

import Common
import Models

class Frame(ceGUI.Frame):
    pass


class Panel(ceGUI.DataGridPanel):
    pass


class Grid(Common.BaseGrid):

    def OnCellSelected(self, event):
        super(Grid, self).OnCellSelected(event)
        origRow = self.GetRow()
        if origRow is not None and event.Row != self.GridCursorRow:
            if self._RowIsEmpty(origRow):
                self.DeleteRows(self.GridCursorRow)
                return
            for colIndex, column in enumerate(self.table.columns):
                exc = column.VerifyValue(origRow)
                if exc is not None:
                    self.SetGridCursor(self.GridCursorRow, colIndex)
                    self.EnableCellEditControl()
                    raise exc
            handle = self.table.rowHandles[self.GridCursorRow]
            self.table.dataSet.UpdateSingleRow(handle)

    def OnCreate(self):
        super(Grid, self).OnCreate()
        self.GetParent().BindEvent(self, wx.grid.EVT_GRID_TABBING, self.OnTab)

    def OnTab(self, event):
        event.Skip()
        if not event.ShiftDown() and event.Row == self.GetNumberRows() - 1 \
                and event.Col == self.GetNumberCols() - 1:
            self.InsertRows()
            wx.CallAfter(self.GoToCell, event.Row + 1, 0)


class DataSet(ceGUI.DataSet):
    pkIsGenerated = True
    updateTableName = "Donations"
    pkSequenceName = "DonationId_s"
    insertAttrNames = "trayId donatorId cash"
    updateAttrNames = "donatorId cash"

    def InsertRowInDatabase(self, transaction, row):
        item = super(DataSet, self).InsertRowInDatabase(transaction, row)
        setValues = dict(causeId = row.causeId, amount = row.amount,
                donationId = None)
        transaction.AddItem(tableName = "DonationComponents",
                setValues = setValues, referencedItems = [item],
                fkArgs = ["donationId"])
        return item

    def UpdateRowInDatabase(self, transaction, row, origRow):
        super(DataSet, self).UpdateRowInDatabase(transaction, row, origRow)
        setValues = dict(causeId = row.causeId, amount = row.amount)
        transaction.AddItem(tableName = "DonationComponents",
                setValues = setValues,
                conditions = dict(donationId = row.donationId))

