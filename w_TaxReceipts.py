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

    def _CreateContextMenu(self):
        super(List, self)._CreateContextMenu()
        self.menu.AddSeparator()
        self.printReceiptsMenuItem = self.menu.AddEntry(self,
                "Print Receipts", method = self.OnPrintReceipts,
                passEvent = False)

    def OnContextMenu(self):
        selectedItems = self.GetSelectedItems()
        self.printReceiptsMenuItem.Enable(len(selectedItems) > 0)
        super(List, self).OnContextMenu()

    def OnCreate(self):
        self.AddColumn("receiptNumber", "Num", 75)
        self.AddColumn("name", "Name", 250, cls = Common.NameColumn)
        self.AddColumn("amount", "Amount", cls = Common.AmountColumn,
                justification = wx.LIST_FORMAT_RIGHT)

    def OnPrintReceipts(self):
        cls = ceGUI.GetModuleItem("r_TaxReceipts", "Report")
        report = cls(self)
        year, = self.dataSet.retrievalArgs
        report.Print(year, self.GetSelectedItems())


class DataSet(ceDatabase.DataSet):
    tableName = "TaxReceipts"
    attrNames = "receiptNumber donatorId amount dateIssued isDuplicate"
    charBooleanAttrNames = "isDuplicate"
    pkAttrNames = "receiptNumber"
    sortByAttrNames = "receiptNumber"
    retrievalAttrNames = "year"

