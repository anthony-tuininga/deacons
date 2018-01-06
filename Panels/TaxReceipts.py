"""
Panel displaying the tax receipts for a given year.
"""

import ceGUI

import Common
import Models

class Panel(Common.BasePanel):
    pass


class Grid(Common.BaseGrid):

    def _CreateContextMenu(self):
        super(Grid, self)._CreateContextMenu()
        self.menu.AddSeparator()
        self.printReceiptsMenuItem = self.menu.AddEntry(self,
                "Print Receipts", method = self.OnPrintReceipts,
                passEvent = False)

    def OnContextMenu(self):
        selectedItems = self.GetSelectedItems()
        self.printReceiptsMenuItem.Enable(len(selectedItems) > 0)
        super(Grid, self).OnContextMenu()

    def OnCreate(self):
        self.AddColumn("receiptNumber", "Num", defaultWidth = 75)
        self.AddColumn("name", "Name", defaultWidth = 250,
                cls = Common.ColumnName)
        self.AddColumn("amount", "Amount", cls = ceGUI.ColumnMoney)

    def OnInsertRow(self, row, choice):
        row.year = self.config.year

    def OnPrintReceipts(self):
        year, = self.dataSet.retrievalArgs
        cls = ceGUI.GetModuleItem("ReportDefs.TaxReceipts", "Report")
        args = (year, self.GetSelectedItems())
        report = cls()
        report.Preview(args)


class DataSet(ceGUI.DataSet):
    rowClass = Models.TaxReceipts

    def _GetRows(self):
        return [r for r in self.config.GetCachedRows(self.rowClass) \
                if r.year == self.config.year]

