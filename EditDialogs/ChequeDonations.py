"""
Frame for editing cheque donations.
"""

import ceGUI

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

    def _RowIsEmpty(self, row):
        return row.donatorId is None and row.causeId is None and \
                row.amount == 0

    def OnCreate(self):
        super(Grid, self).OnCreate()
        self.AddColumn("donatorId", "Donator", defaultWidth = 300,
                cls = Common.ColumnDonatorName, required = True)
        self.AddColumn("causeId", "Cause", defaultWidth = 200,
                cls = Common.ColumnCauseDescription, required = True)
        self.AddColumn("amount", "Amount", defaultWidth = 200,
                cls = ceGUI.ColumnMoney, required = True)


class DataSet(BaseDonations.DataSet):
    rowClass = Models.Donations
    retrievalAttrNames = "trayId cash"

