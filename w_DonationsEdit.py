"""
Dialog for editing donations.
"""

import ceDatabase
import ceGUI
import decimal
import wx

import Common

class Dialog(ceGUI.StandardDialog):

    def OnCreate(self):
        self.grid = Grid(self)
        parent = self.GetParent()
        self.collection = parent.list.contextItem
        title = "Edit Donations - %s" % \
                self.collection.dateCollected.strftime("%A, %B %d, %Y")
        self.SetTitle(title)
        self.grid.Retrieve(self.collection.collectionId)
        self.grid.table.dataSet.claimYear = self.collection.dateCollected.year

    def OnLayout(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.grid, flag = wx.EXPAND | wx.ALL, proportion = 1,
                border = 5)
        return sizer

    def RestoreSettings(self):
        self.grid.RestoreColumnWidths()

    def SaveSettings(self):
        self.grid.SaveColumnWidths()


class Grid(ceGUI.Grid):

    def OnCreate(self):
        self.AddColumn(GridColumnAssignedNumber, "Number", "assignedNumber")
        self.AddColumn(GridColumnName, "Name", "name")
        self.AddColumn(GridColumnCause, "Cause", "causeId")
        self.AddColumn(ceGUI.GridColumnBool, "Cash", "cash")
        self.AddColumn(GridColumnAmount, "Amount", "amount")


class GridColumnAmount(ceGUI.GridColumn):

    def _Initialize(self):
        self.attr.SetAlignment(wx.ALIGN_RIGHT, wx.ALIGN_CENTRE)

    def GetValue(self, row):
        return Common.FormattedAmount(row.amount)


class GridColumnAssignedNumber(ceGUI.GridColumn):

    def GetSortValue(self, row):
        return None

    def GetValue(self, row):
        return ""


class GridColumnCause(ceGUI.GridColumn):

    def GetSortValue(self, row):
        if row.causeId is not None:
            cause = self.config.cache.CauseForId(row.causeId)
            return cause.description.upper()

    def GetValue(self, row):
        if row.causeId is None:
            return ""
        cause = self.config.cache.CauseForId(row.causeId)
        return cause.description


class GridColumnName(ceGUI.GridColumn):

    def GetSortValue(self, row):
        if row.donatorId is not None:
            donator = self.config.cache.DonatorForId(row.donatorId)
            return donator.name.upper()

    def GetValue(self, row):
        if row.donatorId is None:
            return ""
        donator = self.config.cache.DonatorForId(row.donatorId)
        return donator.name


class DataSet(ceDatabase.DataSet):
    tableName = "Donations"
    attrNames = """donationId causeId claimYear amount cash donatorId
            splitDonationId"""
    charBooleanAttrNames = "cash"
    pkAttrNames = "donationId"
    retrievalAttrNames = "collectionId"
    pkSequenceName = "DonationId_s"
    pkIsGenerated = True

    def _OnInsertRow(self, row, choice):
        row.amount = decimal.Decimal("0.00")
        row.claimYear = self.claimYear
        row.cash = False

