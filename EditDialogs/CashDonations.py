"""
Frame for editing cash donations.
"""

import ceGUI

from . import BaseDonations

import Common
import Models

class Frame(BaseDonations.Frame):
    hasToolbar = hasMenus = False
    defaultSize = (650, 700)
    title = "Edit Cash Donations"


class TopPanel(BaseDonations.TopPanel):
    pass


class BottomPanel(BaseDonations.BottomPanel):

    def GetRetrievalArgs(self):
        return [self.tray.trayId, True]


class Grid(BaseDonations.Grid):

    def _RowIsEmpty(self, row):
        return row.donatorId is None and row.amount == 0

    def OnCreate(self):
        parent = self.GetParent()
        self.tray = parent.tray
        self.AddColumn("donatorId", "Donator", defaultWidth = 300,
                cls = Common.ColumnDonatorName, required = True)
        self.AddColumn("amount", "Amount", defaultWidth = 200,
                cls = ceGUI.ColumnMoney, required = True)
        super(Grid, self).OnCreate()


class DataSet(BaseDonations.DataSet):
    rowClass = Models.Donations
    retrievalAttrNames = "trayId cash"

