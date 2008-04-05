"""
Dialog for editing split donations.
"""

import ceDatabase
import ceGUI
import decimal
import wx

import Common

class Dialog(Common.DonationsDialog):
    title = "Edit Split Donation"

    def _RowIsEmpty(self, row):
        return row.causeId is None and row.amount == 0

    def _SetAmountField(self):
        formattedAmount = Common.FormattedAmount(self.splitDonation.amount)
        self.amountField.SetValue(formattedAmount)

    def OnCreate(self):
        self.nameLabel = self.AddLabel("Name:")
        self.nameField = self.AddTextField(style = wx.TE_READONLY)
        self.amountLabel = self.AddLabel("Amount:")
        self.amountField = self.AddTextField(style = wx.TE_READONLY)
        self.grid = Grid(self)
        super(Dialog, self).OnCreate()

    def OnLayout(self):
        fieldsSizer = self.CreateFieldLayout(self.nameLabel, self.nameField,
                self.amountLabel, self.amountField)
        sizer = super(Dialog, self).OnLayout()
        sizer.Insert(0, fieldsSizer, border = 5, flag = wx.EXPAND | wx.ALL)
        return sizer

    def OnOk(self):
        super(Dialog, self).OnOk()
        self.splitDonation.donations = self.grid.table.dataSet.rows.values()

    def Setup(self, collection, splitDonation, causes):
        self.splitDonation = splitDonation
        donator = self.config.cache.DonatorForId(splitDonation.donatorId)
        self.nameField.SetValue(donator.name)
        self._SetAmountField()
        self.grid.table.dataSet.Setup(collection, splitDonation, causes)
        self.grid.Retrieve()
        if len(self.grid.table.rowHandles) == 0:
            self.grid.InsertRows(0)


class Grid(ceGUI.Grid):
    sortOnRetrieve = False

    def DeleteRows(self, rowIndex, numRows = 1):
        row = self.table.GetRow(rowIndex)
        super(Grid, self).DeleteRows(rowIndex, numRows)
        splitDonation = self.table.dataSet.splitDonation
        splitDonation.amount -= row.amount
        parent = self.GetParent()
        parent._SetAmountField()

    def OnCreate(self):
        self.AddColumn("causeId", "Cause", 175, cls = Common.GridColumnCause,
                required = True)
        self.AddColumn("amount", "Amount", cls = GridColumnAmount)


class GridColumnAmount(Common.GridColumnAmount):

    def SetValue(self, grid, dataSet, rowHandle, row, rawValue):
        origValue = row.amount
        returnValue = super(GridColumnAmount, self).SetValue(grid, dataSet,
                rowHandle, row, rawValue)
        dataSet.splitDonation.amount += (row.amount - origValue)
        formattedAmount = Common.FormattedAmount(dataSet.splitDonation.amount)
        parent = grid.GetParent()
        parent.amountField.SetValue(formattedAmount)
        return returnValue


class DataSet(Common.DonationsDataSet):

    def _GetRows(self, ignored):
        return self.splitDonation.donations

    def _OnInsertRow(self, row, choice):
        super(DataSet, self)._OnInsertRow(row, choice)
        row.donatorId = self.splitDonation.donatorId
        row.splitDonationId = self.splitDonation.splitDonationId

    def Setup(self, collection, splitDonation, causes):
        self.contextItem = collection
        self.splitDonation = splitDonation
        self.causes = causes

