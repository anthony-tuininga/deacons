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
        self.AddColumn("assignedNumber", "Number", 70,
                cls = GridColumnAssignedNumber)
        self.AddColumn("name", "Name", 220, cls = GridColumnName)
        self.AddColumn("causeId", "Cause", 175, cls = GridColumnCause)
        self.AddColumn("cash", "Cash", 65, cls = ceGUI.GridColumnBool)
        self.AddColumn("amount", "Amount", cls = GridColumnAmount)


class GridColumnAmount(ceGUI.GridColumn):
    defaultHorizontalAlignment = wx.ALIGN_RIGHT

    def GetValue(self, row):
        return Common.FormattedAmount(row.amount)


class GridColumnAssignedNumber(ceGUI.GridColumnInt):

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
            return (donator.lastName.upper(), donator.givenNames.upper())

    def GetValue(self, row):
        if row.donatorId is None:
            return ""
        donator = self.config.cache.DonatorForId(row.donatorId)
        return "%s, %s" % (donator.lastName, donator.givenNames)


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

