"""
Print a report that is placed in the bulletin each quarter.
"""

import datetime
import wx

import Common
import Reports

class Report(Reports.Report):

    def __GetAmounts(self, yearStart, quarterStart, quarterEnd):
        cursor = self.connection.cursor()
        cursor.execute("""
                select
                  c.Description,
                  ( select sum(ca.ChequeAmount + ca.CashAmount)
                    from
                      Collections ct
                      join CollectionAmounts ca
                          on ca.CollectionId = ct.CollectionId
                    where ct.DateCollected between ? and ?
                      and ca.CauseId = c.CauseId
                  ),
                  ( select sum(ca.ChequeAmount + ca.CashAmount)
                    from
                      Collections ct
                      join CollectionAmounts ca
                          on ca.CollectionId = ct.CollectionId
                    where ct.DateCollected between ? and ?
                      and ca.CauseId = c.CauseId
                  )
                from Causes c
                where IsReported = 't'""",
                quarterStart, quarterEnd, yearStart, quarterEnd)
        return cursor.fetchall()

    def __PrintBudget(self, outFile, quarterEnd, budgetAmount, description,
            quarterAmount, yearAmount):
        print >> outFile, description.ljust(27),
        print >> outFile, "Quarter".center(14),
        print >> outFile, "Year to Date"
        requiredYearToDate = budgetAmount * (quarterEnd.month / 12.0)
        print >> outFile, "Required".ljust(27),
        amount = budgetAmount / 4.0
        print >> outFile, Common.FormattedAmount(amount).rjust(13),
        print >> outFile, Common.FormattedAmount(requiredYearToDate).rjust(13)
        print >> outFile, "Collected".ljust(27),
        print >> outFile, Common.FormattedAmount(quarterAmount).rjust(13),
        print >> outFile, Common.FormattedAmount(yearAmount).rjust(13)
        print >> outFile

    def __PrintCauses(self, outFile, quarterEnd, amounts):
        print >> outFile, "Causes".ljust(27),
        print >> outFile, "Quarter".center(14),
        print >> outFile, "Year to Date"
        for description, quarterAmount, yearAmount in sorted(amounts):
            print >> outFile, description.ljust(27),
            print >> outFile, Common.FormattedAmount(quarterAmount).rjust(13),
            print >> outFile, Common.FormattedAmount(yearAmount).rjust(13)

    def _GetPrintArgs(self):
        dialog = self.parentWindow.OpenWindow("w_SelectDate.Dialog")
        proceed = (dialog.ShowModal() == wx.ID_OK)
        dialog.Destroy()
        if not proceed:
            return
        date = dialog.GetDate()
        quarterNum = (date.month - 1) / 3 + 1
        defaultFileName = "report-%d-Q%d.txt" % (date.year, quarterNum)
        dialog = wx.FileDialog(parent = self.parentWindow,
                defaultFile = defaultFileName, style = wx.SAVE)
        proceed = (dialog.ShowModal() == wx.ID_OK)
        fileName = dialog.GetPath()
        dialog.Destroy()
        if not proceed:
            return
        yearStart = datetime.date(date.year, 1, 1)
        quarterStartMonth = ((date.month - 1) / 3) * 3 + 1
        quarterStart = datetime.date(date.year, quarterStartMonth, 1)
        if quarterStartMonth == 10:
            nextStart = datetime.date(date.year + 1, 1, 1)
        else:
            nextStart = datetime.date(date.year, quarterStartMonth + 3, 1)
        quarterEnd = nextStart - datetime.timedelta(1)
        return yearStart, quarterStart, quarterEnd, fileName

    def _Print(self, yearStart, quarterStart, quarterEnd, fileName):
        outFile = file(fileName, "w")
        print >> outFile, "Quarter Start:", quarterStart
        print >> outFile, "Quarter End:", quarterEnd
        print >> outFile
        budgetAmount = self.GetBudgetAmountForYear(yearStart.year)
        amounts = self.__GetAmounts(yearStart, quarterStart, quarterEnd)
        budgetAmounts, = [r for r in amounts if r[0] == "Budget"]
        causeAmounts = [r for r in amounts if r[0] != "Budget"]
        self.__PrintBudget(outFile, quarterEnd, budgetAmount, *budgetAmounts)
        self.__PrintCauses(outFile, quarterEnd, causeAmounts)

