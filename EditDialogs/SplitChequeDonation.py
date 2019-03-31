"""
Frame for editing split cheque donations.
"""

import ceGUI

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
        super(Frame, self).OnCreate()


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

    def _RowIsEmpty(self, row):
        return row.causeId is None and row.amount == 0

    def OnCreate(self):
        super(Grid, self).OnCreate()
        self.AddColumn("causeId", "Cause", defaultWidth = 200,
                cls = Common.ColumnCauseDescription, required = True)
        self.AddColumn("amount", "Amount", defaultWidth = 200,
                cls = ceGUI.ColumnMoney, required = True)

    def OnInsertRow(self, row, choice):
        parent = self.GetParent().GetParent()
        row.donationId = parent.donation.donationId
        row.amount = 0


class DataSet(ceGUI.DataSet):
    rowClass = Models.DonationComponents
    retrievalAttrNames = "donationId"
