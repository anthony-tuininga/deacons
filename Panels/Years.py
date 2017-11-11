"""
Panel displaying information about years.
"""

import ceGUI
import cx_Logging
import datetime
import wx

import Common
import Models

class Panel(ceGUI.DataListPanel):
    editDialogName = "EditDialogs.Years.Dialog"


class List(ceGUI.DataList):

    def __AskQuestion(self, message, title):
        dialog = wx.MessageDialog(self, message, title,
                wx.YES_NO | wx.ICON_QUESTION)
        response = dialog.ShowModal()
        dialog.Destroy()
        return (response == wx.ID_YES)

    def __CheckReceipts(self, row):
        if not row.promptForReceiptGeneration:
            return
        message = "Calculate tax receipts for year %d?" % row.year
        if self.__AskQuestion(message, "Calculate Tax Receipts?"):
            self.__GenerateReceipts(row)
            return
        message = "Do not ask about calculating tax receipts for %s again?" % \
                row.year
        if self.__AskQuestion(message, "Ask About Receipt Calculation?"):
            cursor = self.config.connection.cursor()
            cursor.execute("""
                    update Years set
                        PromptForReceiptGeneration = 'f'
                    where Year = ?""", row.year)
            self.config.connection.commit()
            row.promptForReceiptGeneration = False

    def __GenerateReceipts(self, row):
        cx_Logging.Debug("generating receipts for year %s", row.year)
        origReceipts = self.__GetOriginalReceipts(row)
        cx_Logging.Debug("%s original receipts", len(origReceipts))
        maxReceiptNum = self.__GetNextReceiptNum()
        cx_Logging.Debug("max receipt number is %s", maxReceiptNum)
        donatedAmounts = self.__GetDonatedAmounts(row)
        cx_Logging.Debug("%s donations to receipt", len(donatedAmounts))
        today = datetime.date.today().strftime("%Y-%m-%d")
        receiptsCanceled = receiptsUpdated = receiptsCreated = 0
        cursor = self.config.connection.cursor()
        for name, donatorId, amount in donatedAmounts:
            if donatorId in origReceipts:
                origReceiptNumber, origAmount = origReceipts[donatorId]
            else:
                origReceiptNumber = origAmount = None
            if amount == origAmount:
                continue
            if row.receiptsIssued and origAmount is not None:
                receiptsCanceled += 1
                cursor.execute("""
                        update TaxReceipts set
                            Canceled = 't'
                        where ReceiptNumber = ?""", origReceiptNumber)
            if not row.receiptsIssued and origAmount is not None:
                receiptsUpdated += 1
                cursor.execute("""
                        update TaxReceipts set
                            Amount = ?
                        where ReceiptNumber = ?""",
                        Common.FormattedAmount(amount), origReceiptNumber)
            else:
                receiptsCreated += 1
                maxReceiptNum += 1
                formattedAmount = Common.FormattedAmount(amount)
                cursor.execute("""
                        insert into TaxReceipts
                        (ReceiptNumber, Year, DonatorId, Amount, Canceled,
                         DateIssued, IsDuplicate)
                        values (?, ?, ?, ?, 'f', ?, 'f')""",
                        maxReceiptNum, row.year, donatorId, formattedAmount,
                        today)
        self.config.connection.commit()
        message = "%d canceled. %d updated. %d created" % \
                (receiptsCanceled, receiptsUpdated, receiptsCreated)
        wx.MessageBox(message, "Receipt Generation Results",
                wx.OK | wx.ICON_INFORMATION, self)

    def __GetDonatedAmounts(self, row):
        cursor = self.config.connection.cursor()
        cursor.execute("""
                select
                  d.DonatorId,
                  sum(d.Amount)
                from
                  CausesForYear cy,
                  Donations d
                where d.ClaimYear = ?
                  and d.DonatorId is not null
                  and cy.CauseId = d.CauseId
                  and cy.Year = d.ClaimYear
                  and cy.Deductible = 't'
                group by d.DonatorId""",
                row.year)
        amounts = []
        for donatorId, amount in cursor:
            donator = self.config.cache.DonatorForId(donatorId)
            amounts.append((donator.name, donatorId, amount))
        amounts.sort()
        return amounts

    def __GetNextReceiptNum(self):
        cursor = self.config.connection.cursor()
        cursor.execute("""
                select max(ReceiptNumber)
                from TaxReceipts""")
        maxReceiptNum, = cursor.fetchone()
        return maxReceiptNum

    def __GetOriginalReceipts(self, row):
        origReceipts = {}
        cursor = self.config.connection.cursor()
        cursor.execute("""
                select
                  ReceiptNumber,
                  DonatorId,
                  Amount
                from TaxReceipts
                where Year = ?
                  and Canceled = 'f'""",
                row.year)
        for receiptNumber, donatorId, amount in cursor:
            origReceipts[donatorId] = (receiptNumber, amount)
        return origReceipts

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
        self.AddColumn("budgetAmount", "Budget Amount", rightJustified = True,
                cls = Common.AmountColumn)
        self.AddColumn("receiptsIssued", "Receipts Issued",
                cls = ceGUI.ColumnBool)

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
        item, = self.GetSelectedItems()
        self.__CheckReceipts(item)
        app.topWindow._AddTaxReceiptsPage(item.year)


class DataSet(ceGUI.DataSet):
    rowClass = Models.Years

