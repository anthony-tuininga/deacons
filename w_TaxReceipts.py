"""
Panel displaying the tax receipts for a given year.
"""

import ceDatabase
import ceGUI
import wx

import Common

class Panel(ceGUI.DataListPanel):
    pass


class List(ceGUI.DataList):
    singleSelection = False

    def OnCreate(self):
        self.AddColumn("receiptNumber", "Num", 75)
        self.AddColumn("name", "Name", 250, cls = Common.NameColumn)
        self.AddColumn("amount", "Amount", cls = Common.AmountColumn,
                justification = wx.LIST_FORMAT_RIGHT)


class DataSet(ceDatabase.DataSet):
    tableName = "TaxReceipts"
    attrNames = "receiptNumber donatorId amount"
    pkAttrNames = "receiptNumber"
    sortByAttrNames = "receiptNumber"
    retrievalAttrNames = "year"

