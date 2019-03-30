"""
Base frame for editing donations. Note that a frame used instead of a dialog
because otherwise some of the key events on the grid are swallowed!
"""

import ceGUI
import wx

import Common
import Models

class Frame(ceGUI.Frame):

    def OnCreate(self):
        parent = self.GetParent()
        self.tray, = parent.grid.GetSelectedItems()
        cls = self._GetClass("TopPanel")
        self.topPanel = cls(self)
        cls = self._GetClass("BottomPanel")
        self.bottomPanel = cls(self)
        super(Frame, self).OnCreate()
        self.topPanel.OnPostCreate()
        self.bottomPanel.grid.SetFocus()

    def OnLayout(self):
        topSizer = wx.BoxSizer(wx.VERTICAL)
        topSizer.Add(self.topPanel, flag = wx.ALL | wx.EXPAND, border = 5)
        topSizer.Add(self.bottomPanel, flag = wx.EXPAND, proportion = 1)
        return topSizer


class TopPanel(ceGUI.DataEditPanel):

    def _GetDataSet(self):
        parent = self.GetParent()
        self.tray = parent.tray
        app = ceGUI.GetApp()
        dataSet = TopPanelDataSet(app.config.dataSource)
        dataSet.SetRows([self.tray])
        return dataSet

    def OnCreate(self):
        self.AddColumn("dateCollected", "Date Collected:",
                constantValue = self.tray.dateCollected.strftime("%B %d, %Y"))
        self.AddColumn("dateDeposited", "Date Deposited:",
                constantValue = self.tray.dateDeposited.strftime("%B %d, %Y"))
        cause = self.config.GetCachedRowByPK(Models.Causes, self.tray.causeId)
        self.AddColumn("causeId", "Cause:", constantValue = cause.description)


class TopPanelDataSet(ceGUI.DataSet):
    rowClass = Models.Trays


class BottomPanel(ceGUI.DataGridPanel):

    def OnCreate(self):
        parent = self.GetParent()
        self.tray = parent.tray
        super(BottomPanel, self).OnCreate()

    def Retrieve(self, refresh):
        super(BottomPanel, self).Retrieve(refresh)
        if self.grid.GetNumberRows() == 0:
            self.grid.InsertRows(0)


class Grid(Common.BaseGrid):
    sortOnRetrieve = False

    def DeleteRows(self, row, numRows = 1):
        super(Grid, self).DeleteRows(row, numRows)
        self.Update()

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
        parent = self.GetParent()
        self.tray = parent.tray
        self.GetParent().BindEvent(self, wx.grid.EVT_GRID_TABBING, self.OnTab)

    def OnInsertRow(self, row, choice):
        row.causeId = self.tray.causeId
        row.cash = False
        row.amount = 0

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

