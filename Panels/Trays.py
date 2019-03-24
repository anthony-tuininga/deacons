"""
Panel which displays trays and enables editing of them.
"""

import ceGUI
import datetime

import Common
import Models

class Panel(Common.BasePanel):

    def GetBaseRows(self):
        return self.grid.dataSet.rowClass.GetRows(self.config.dataSource,
                year = self.config.year)

    def OnCreateFilterArgs(self):
        self.CreateDateDepositedFilterArg()
        self.CreateDateCollectedFilterArg()
        self.CreateCauseFilterArg()

    def OnPopulateBaseRows(self, rows):
        self.SetDateDepositedChoices(rows)
        self.SetDateCollectedChoices(rows)
        self.SetCauseChoices(rows)


class Grid(Common.BaseGrid):

    def _CreateContextMenu(self):
        super(Grid, self)._CreateContextMenu()
        self.menu.AddSeparator()
        self.editCashMenuItem = self.menu.AddEntry(self, "Edit Cash...",
                method = self.OnEditCash, passEvent = False)
        self.editCashDonationsMenuItem = self.menu.AddEntry(self,
                "Edit Cash Donations...", method = self.OnEditCashDonations,
                passEvent = False)

    def OnContextMenu(self):
        selectedItems = self.GetSelectedItems()
        canEditSubItem = len(selectedItems) == 1 \
                and selectedItems[0].trayId is not None
        self.editCashMenuItem.Enable(canEditSubItem)
        self.editCashDonationsMenuItem.Enable(canEditSubItem)
        super(Grid, self).OnContextMenu()

    def OnCreate(self):
        super(Grid, self).OnCreate()
        self.AddColumn("dateDeposited", "Deposited", defaultWidth = 100,
                cls = ceGUI.ColumnDate, required = True)
        self.AddColumn("dateCollected", "Collected", defaultWidth = 100,
                cls = ceGUI.ColumnDate, required = True)
        self.AddColumn("causeId", "Cause", defaultWidth = 200,
                cls = Common.ColumnCauseDescription, required = True)
        self.AddColumn("chequeAmount", "Cheque Amount", defaultWidth = 200,
                cls = ceGUI.ColumnMoney, readOnly = True)
        self.AddColumn("cashAmount", "Cash Amount", defaultWidth = 200,
                cls = ceGUI.ColumnMoney, readOnly = True)

    def OnEditCash(self):
        selectedRow, = self.GetSelectedItems()
        with self.GetParent().OpenWindow("EditDialogs.Cash.Dialog",
                parentItem = selectedRow) as dialog:
            dialog.ShowModalOk()

    def OnEditCashDonations(self):
        dialogName = "EditDialogs.CashDonations.Frame"
        frame = self.GetParent().OpenWindow(dialogName)
        frame.Show()

    def OnInsertRow(self, row, choice):
        row.dateDeposited = datetime.datetime.today()
        row.chequeAmount = 0
        row.cashAmount = 0


class DataSet(ceGUI.DataSet):
    rowClass = Models.Trays
    updateTableName = "Trays"
    pkSequenceName = "TrayId_s"
    pkIsGenerated = True
    insertAttrNames = "dateDeposited dateCollected causeId"
    updateAttrNames = "dateDeposited dateCollected causeId"

    def _GetRows(self, rows, datesDeposited, datesCollected, causeIds):
        if datesDeposited:
            rows = [r for r in rows if r.dateDeposited in datesDeposited]
        if datesCollected:
            rows = [r for r in rows if r.dateCollected in datesCollected]
        if causeIds:
            rows = [r for r in rows if r.causeId in causeIds]
        return rows

