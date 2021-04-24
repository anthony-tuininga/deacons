"""
Frame for editing split cheque donations.
"""

import ceGUI
import decimal

from . import BaseDonations

import Common
import Models

class Frame(BaseDonations.Frame):
    hasToolbar = hasMenus = False
    defaultSize = (650, 700)
    title = "Edit Split Cheque Donation"

    def GetTray(self):
        parent = self.GetParent()
        return parent.tray

    def OnCreate(self):
        parent = self.GetParent()
        self.donation, = parent.grid.GetSelectedItems()
        super().OnCreate()

    def OnSplitAmountsChanged(self):
        grid = self.bottomPanel.grid
        total_amount = decimal.Decimal(0)
        for row in grid.table.GetRows(0, grid.table.GetNumberRows()):
            total_amount += decimal.Decimal(row.amount)
        formatted_amount = "${0:,.2f}".format(total_amount)
        self.topPanel.totalAmountColumn.field.SetValue(formatted_amount)


class TopPanel(BaseDonations.TopPanel):

    def OnCreate(self):
        parent = self.GetParent()
        donation = parent.donation
        self.AddColumn("dateCollected", "Date Collected:",
                constantValue = self.tray.dateCollected.strftime("%B %d, %Y"))
        self.AddColumn("dateDeposited", "Date Deposited:",
                constantValue = self.tray.dateDeposited.strftime("%B %d, %Y"))
        donator = self.config.GetCachedRowByPK(Models.Donators,
                donation.donatorId)
        self.AddColumn("donatorId", "Donator:", constantValue = donator.name)
        self.totalAmountColumn = self.AddColumn("amount", "Amount:",
                constantValue = "${0:,.2f}".format(donation.amount))


class BottomPanel(BaseDonations.BottomPanel):

    def GetRetrievalArgs(self):
        parent = self.GetParent()
        return [parent.donation.donationId]


class Grid(BaseDonations.Grid):
    customCellAttributes = True

    def _RowIsEmpty(self, row):
        return row.causeId is None and row.amount == 0

    def DeleteRows(self, pos=None, numRows=1):
        super().DeleteRows(pos, numRows)
        parent = self.GetParent().GetParent()
        parent.OnSplitAmountsChanged()

    def OnCreate(self):
        super().OnCreate()
        self.AddColumn("causeId", "Cause", defaultWidth = 200,
                cls = Common.ColumnCauseDescription, required = True)
        self.AddColumn("amount", "Amount", defaultWidth = 200,
                cls = SplitAmountColumn, required = True)

    def OnGetCustomCellAttributes(self, row, column, attr):
        if not row.isNew and column.attrName == "causeId":
            attr.SetReadOnly()

    def OnInsertRow(self, row, choice):
        parent = self.GetParent().GetParent()
        row.donationId = parent.donation.donationId
        row.amount = 0
        row.isNew = True


class SplitAmountColumn(ceGUI.ColumnMoney):

    def SetValue(self, grid, dataSet, rowHandle, row, value):
        super().SetValue(grid, dataSet, rowHandle, row,
                                                value)
        parent = grid.GetParent().GetParent()
        parent.OnSplitAmountsChanged()


class DataSet(ceGUI.DataSet):
    rowClass = Models.DonationComponents
    retrievalAttrNames = "donationId"

    def InsertRowInDatabase(self, transaction, row):
        super().InsertRowInDatabase(transaction, row)
        row.isNew = False
