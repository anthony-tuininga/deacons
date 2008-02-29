import ceDatabase
import ceGUI
import wx

import Common

class Panel(ceGUI.DataListPanel):
    editDialogName = "w_YearEdit.Dialog"


class List(ceGUI.DataList):

    def _CreateContextMenu(self):
        super(List, self)._CreateContextMenu()
        self.menu.AppendSeparator()
        self.donatorsMenuItem = self._AddMenuItem(self.menu, "Donators",
                method = self.OnDonators, passEvent = False)
        self.taxReceiptsMenuItem = self._AddMenuItem(self.menu,
                "Tax Receipts", method = self.OnTaxReceipts,
                passEvent = False)

    def OnContextMenu(self):
        self.donatorsMenuItem.Enable(self.contextItem is not None)
        self.taxReceiptsMenuItem.Enable(self.contextItem is not None)
        super(List, self).OnContextMenu()

    def OnCreate(self):
        self.AddColumn("year", "Year", 50)
        self.AddColumn("budgetAmount", "Budget Amount",
                justification = wx.LIST_FORMAT_RIGHT,
                cls = Common.AmountColumn)

    def OnDonators(self):
        app = wx.GetApp()
        app.topWindow._AddDonatorsForYearPage(self.contextItem.year)

    def OnTaxReceipts(self):
        app = wx.GetApp()
        app.topWindow._AddTaxReceiptsPage(self.contextItem.year)


class DataSet(ceDatabase.DataSet):
    tableName = "Years"
    attrNames = "year budgetAmount"
    pkAttrNames = "year"

