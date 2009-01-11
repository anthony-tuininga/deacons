import ceDatabase
import ceGUI
import wx

import Common

class Panel(ceGUI.DataListPanel):
    editDialogName = "w_YearEdit.Dialog"


class List(ceGUI.DataList):

    def _CreateContextMenu(self):
        super(List, self)._CreateContextMenu()
        self.menu.AddSeparator()
        self.causesMenuItem = self.menu.AddEntry(self, "Causes",
                method = self.OnCauses, passEvent = False)
        self.donatorsMenuItem = self.menu.AddEntry(self, "Donators",
                method = self.OnDonators, passEvent = False)
        self.taxReceiptsMenuItem = self.menu.AddEntry(self, "Tax Receipts",
                method = self.OnTaxReceipts, passEvent = False)

    def OnContextMenu(self):
        enabled = (len(self.GetSelectedItems()) == 1)
        self.causesMenuItem.Enable(enabled)
        self.donatorsMenuItem.Enable(enabled)
        self.taxReceiptsMenuItem.Enable(enabled)
        super(List, self).OnContextMenu()

    def OnCreate(self):
        self.AddColumn("year", "Year", 50)
        self.AddColumn("budgetAmount", "Budget Amount",
                justification = wx.LIST_FORMAT_RIGHT,
                cls = Common.AmountColumn)

    def OnCauses(self):
        app = wx.GetApp()
        selectedItems = self.GetSelectedItems()
        app.topWindow._AddCausesForYearPage(selectedItems[0].year)

    def OnDonators(self):
        app = wx.GetApp()
        selectedItems = self.GetSelectedItems()
        app.topWindow._AddDonatorsForYearPage(selectedItems[0].year)

    def OnTaxReceipts(self):
        app = wx.GetApp()
        selectedItems = self.GetSelectedItems()
        app.topWindow._AddTaxReceiptsPage(selectedItems[0].year)


class DataSet(ceDatabase.DataSet):
    tableName = "Years"
    attrNames = "year budgetAmount"
    pkAttrNames = "year"

