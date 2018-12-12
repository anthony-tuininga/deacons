"""
Panel displaying the tax receipts for a given year.
"""

import ceGUI
import cx_Logging
import datetime
import wx

import Common
import Models

class Panel(Common.BasePanel):
    pass


class Grid(Common.BaseGrid):

    def __GetDonatedAmounts(self):
        donators = Models.Donators.GetRows(self.config.dataSource,
                year = self.config.year)
        donatorDict = dict((d.donatorId, d) for d in donators)
        rows = self.config.dataSource.GetRowsDirect("""
                select
                    dc.DonatorId,
                    sum(dc.Amount)
                from
                    Donators d
                    join DonationComponents dc
                        on dc.DonatorId = d.DonatorId
                    join Causes c
                        on c.CauseId = dc.CauseId
                        and c.Deductible = 't'
                where d.Year = ?
                group by dc.DonatorId
                having sum(dc.Amount) > '$0'""", (self.config.year,))
        tempAmounts = []
        for donatorId, amount in rows:
            donator = donatorDict[donatorId]
            tempAmounts.append((donator.name, donatorId, amount))
        tempAmounts.sort()
        return [(donatorId, amount) for name, donatorId, amount in tempAmounts]

    def __GetNextReceiptNum(self):
        sql = "select max(ReceiptNumber) from TaxReceipts"
        rows = self.config.dataSource.GetRowsDirect(sql)
        if not rows:
            return 0
        return rows[0][0]

    def __GetOriginalReceipts(self):
        origReceipts = {}
        rows = Models.TaxReceipts.GetRows(self.config.dataSource,
                year = self.config.year)
        return dict((r.donatorId, r) for r in rows)

    def _CreateContextMenu(self):
        super(Grid, self)._CreateContextMenu()
        self.menu.AddSeparator()
        self.generateReceiptsMenuItem = self.menu.AddEntry(self,
                "Generate Receipts", method = self.OnGenerateReceipts,
                passEvent = False)
        self.printReceiptsMenuItem = self.menu.AddEntry(self,
                "Print Receipts", method = self.OnPrintReceipts,
                passEvent = False)

    def OnContextMenu(self):
        selectedItems = self.GetSelectedItems()
        self.printReceiptsMenuItem.Enable(len(selectedItems) > 0)
        super(Grid, self).OnContextMenu()

    def OnCreate(self):
        super(Grid, self).OnCreate()
        self.AddColumn("receiptNumber", "Num", defaultWidth = 75)
        self.AddColumn("name", "Name", defaultWidth = 250,
                cls = Common.ColumnDonatorName)
        self.AddColumn("amount", "Amount", cls = ceGUI.ColumnMoney)
        self.AddColumn("dateIssued", "Date Issued", cls = ceGUI.ColumnDate,
                defaultWidth = 250)
        self.AddColumn("isDuplicate", "Duplicate?", cls = ceGUI.ColumnBool,
                defaultWidth = 100)
        self.AddColumn("canceled", "Canceled?", cls = ceGUI.ColumnBool,
                defaultWidth = 100)

    def OnGenerateReceipts(self):
        with ceGUI.BusyCursorContext(self):
            cx_Logging.Debug("generating receipts for year %s",
                    self.config.year)
            yearRow = Models.Years.GetRow(self.config.dataSource,
                    year = self.config.year)
            origReceiptDict = self.__GetOriginalReceipts()
            cx_Logging.Debug("%s original receipts", len(origReceiptDict))
            maxReceiptNum = self.__GetNextReceiptNum()
            cx_Logging.Debug("max receipt number is %s", maxReceiptNum)
            donatedAmounts = self.__GetDonatedAmounts()
            cx_Logging.Debug("%s donations to receipt", len(donatedAmounts))
            receiptsCanceled = receiptsUpdated = receiptsCreated = 0
            cursor = self.config.dataSource.connection.cursor()
            for donatorId, amount in donatedAmounts:
                origReceipt = origReceiptDict.get(donatorId)
                if origReceipt is not None and origReceipt.amount == amount:
                    continue
                if yearRow.receiptsIssued and origReceipt is not None:
                    receiptsCanceled += 1
                    cursor.execute("""
                            update TaxReceipts set
                                Canceled = 't'
                            where ReceiptNumber = ?""",
                            origReceipt.receiptNumber)
                if not yearRow.receiptsIssued and origReceipt is not None:
                    receiptsUpdated += 1
                    cursor.execute("""
                            update TaxReceipts set
                                Amount = ?
                            where ReceiptNumber = ?""",
                            amount, origReceipt.receiptNumber)
                else:
                    receiptsCreated += 1
                    maxReceiptNum += 1
                    cursor.execute("""
                            insert into TaxReceipts
                            (ReceiptNumber, Year, DonatorId, Amount, Canceled,
                                    DateIssued, IsDuplicate)
                            values (?, ?, ?, ?, 'f', ?, 'f')""",
                            maxReceiptNum, yearRow.year, donatorId, amount,
                            datetime.date.today())
            cursor.connection.commit()
        message = "%d canceled. %d updated. %d created." % \
                (receiptsCanceled, receiptsUpdated, receiptsCreated)
        wx.MessageBox(message, "Receipt Generation Results",
                wx.OK | wx.ICON_INFORMATION, self)
        if receiptsCanceled or receiptsUpdated or receiptsCreated:
            self.config.GetCachedRows(self.dataSet.rowClass, refresh = True)
            self.Retrieve()

    def OnInsertRow(self, row, choice):
        row.year = self.config.year

    def OnPrintReceipts(self):
        receipts = self.GetSelectedItems()
        for receipt in receipts:
            receipt.donator = self.config.GetCachedRowByPK(Models.Donators,
                    receipt.donatorId)
        self.config.GeneratePDF("TaxReceipts.rml", receipts = receipts)


class DataSet(ceGUI.DataSet):
    rowClass = Models.TaxReceipts

    def _GetRows(self):
        return [r for r in self.config.GetCachedRows(self.rowClass) \
                if r.year == self.config.year]

