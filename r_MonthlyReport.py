"""
Print a report that is placed in the bulletin each month.
"""

import datetime
import wx

import Common
import Reports

class Report(Reports.Report):

    def __GetAmounts(self, yearStart, monthStart, monthEnd):
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
                monthStart, monthEnd, yearStart, monthEnd)
        return cursor.fetchall()

    def __PrintBudget(self, outFile, monthEnd, budgetAmount, description,
            monthAmount, yearAmount):
        print >> outFile, description.ljust(27),
        print >> outFile, monthEnd.strftime("%B").center(14),
        print >> outFile, "Year to Date"
        requiredYearToDate = budgetAmount * (monthEnd.month / 12.0)
        print >> outFile, "Required".ljust(27),
        formattedAmount = Common.FormattedAmount(budgetAmount / 12.0)
        print >> outFile, formattedAmount.rjust(13),
        print >> outFile, Common.FormattedAmount(requiredYearToDate).rjust(13)
        print >> outFile, "Collected".ljust(27),
        print >> outFile, Common.FormattedAmount(monthAmount).rjust(13),
        print >> outFile, Common.FormattedAmount(yearAmount).rjust(13)
        print >> outFile

    def __PrintCauses(self, outFile, monthEnd, amounts):
        print >> outFile, "Causes".ljust(27),
        print >> outFile, monthEnd.strftime("%B").center(14),
        print >> outFile, "Year to Date"
        for description, monthAmount, yearAmount in sorted(amounts):
            print >> outFile, description.ljust(27),
            print >> outFile, Common.FormattedAmount(monthAmount).rjust(13),
            print >> outFile, Common.FormattedAmount(yearAmount).rjust(13)

    def _GetPrintArgs(self):
        dialog = self.parentWindow.OpenWindow("w_SelectDate.Dialog")
        proceed = (dialog.ShowModal() == wx.ID_OK)
        dialog.Destroy()
        if not proceed:
            return
        date = dialog.GetDate()
        defaultFileName = "report-%.4d-%.2d.txt" % (date.year, date.month)
        dialog = wx.FileDialog(parent = self.parentWindow,
                defaultFile = defaultFileName, style = wx.SAVE)
        proceed = (dialog.ShowModal() == wx.ID_OK)
        fileName = dialog.GetPath()
        dialog.Destroy()
        if not proceed:
            return
        yearStart = datetime.date(date.year, 1, 1)
        monthStart = datetime.date(date.year, date.month, 1)
        if date.month == 12:
            nextMonthStart = datetime.date(date.year + 1, 1, 1)
        else:
            nextMonthStart = datetime.date(date.year, date.month + 1, 1)
        monthEnd = nextMonthStart - datetime.timedelta(1)
        return yearStart, monthStart, monthEnd, fileName

    def _Print(self, yearStart, monthStart, monthEnd, fileName):
        outFile = file(fileName, "w")
        budgetAmount = self.GetBudgetAmountForYear(yearStart.year)
        amounts = self.__GetAmounts(yearStart, monthStart, monthEnd)
        budgetAmounts, = [r for r in amounts if r[0] == "Budget"]
        causeAmounts = [r for r in amounts if r[0] != "Budget"]
        self.__PrintBudget(outFile, monthEnd, budgetAmount, *budgetAmounts)
        self.__PrintCauses(outFile, monthEnd, causeAmounts)

