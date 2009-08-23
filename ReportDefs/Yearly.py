"""
Print a report for the year that is given to the treasurer to reconcile with
his statements.
"""

import datetime
import wx

import Common

class Report(Common.TextReport):

    def __GetAmounts(self, year):
        cursor = self.connection.cursor()
        cursor.execute("""
                select
                  cy.Deductible,
                  c.Description,
                  ( select sum(Amount)
                    from Donations
                    where ClaimYear = cy.Year
                      and CauseId = c.CauseId
                  ),
                  ( select sum(ca.CashAmount - ca.EnvelopeCash)
                    from
                      Collections ct
                      join CollectionAmounts ca
                          on ca.CollectionId = ct.CollectionId
                    where ct.DateCollected between ? and ?
                      and ca.CollectionId = ct.CollectionId
                      and ca.CauseId = c.CauseId
                  )
                from
                  CausesForYear cy
                  join Causes c
                      on c.CauseId = cy.CauseId
                where cy.Year = ?""",
                datetime.date(year, 1, 1),
                datetime.date(year, 12, 31),
                year)
        return list(sorted(cursor))

    def __PrintAmounts(self, outFile, title, amounts, deductible):
        totalDonations = totalLooseCash = 0.0
        print >> outFile, title.center(30),
        print >> outFile, "Donations".center(14),
        print >> outFile, "Loose Cash".center(14),
        print >> outFile, "Total".center(14)
        for isDeductible, description, donations, looseCash in amounts:
            if bool(int(isDeductible)) != deductible:
                continue
            if donations is None:
                donations = 0.0
            totalDonations += donations
            if looseCash is None:
                looseCash = 0.0
            totalLooseCash += looseCash
            total = donations + looseCash
            print >> outFile, description.ljust(30),
            print >> outFile, Common.FormattedAmount(donations).rjust(14),
            print >> outFile, Common.FormattedAmount(looseCash).rjust(14),
            print >> outFile, Common.FormattedAmount(total).rjust(14)
        footer = "Total %s" % title
        total = totalDonations + totalLooseCash
        print >> outFile, footer.rjust(30),
        print >> outFile, Common.FormattedAmount(totalDonations).rjust(14),
        print >> outFile, Common.FormattedAmount(totalLooseCash).rjust(14),
        print >> outFile, Common.FormattedAmount(total).rjust(14)
        print >> outFile
        return totalDonations, totalLooseCash

    def __PrintHeader(self, outFile, year):
        header = "Donations for Year %d" % year
        print >> outFile, header.center(76)
        print >> outFile

    def __PrintFooter(self, outFile, totalDonations, totalLooseCash):
        total = totalDonations + totalLooseCash
        print >> outFile, "GRAND TOTAL".rjust(30),
        print >> outFile, Common.FormattedAmount(totalDonations).rjust(14),
        print >> outFile, Common.FormattedAmount(totalLooseCash).rjust(14),
        print >> outFile, Common.FormattedAmount(total).rjust(14)
        print >> outFile

    def _GetPrintArgs(self, parent):
        dialog = parent.OpenWindow("SelectDialogs.Year.Dialog")
        proceed = (dialog.ShowModal() == wx.ID_OK)
        dialog.Destroy()
        if not proceed:
            return
        year = dialog.GetSelectedItem().year
        defaultFileName = "report-%.4d.txt" % year
        dialog = wx.FileDialog(parent = parent, defaultFile = defaultFileName,
                style = wx.SAVE)
        proceed = (dialog.ShowModal() == wx.ID_OK)
        fileName = dialog.GetPath()
        if not proceed:
            return
        return year, fileName

    def Print(self, parent):
        year, fileName = self._GetPrintArgs(parent)
        outFile = file(fileName, "w")
        amounts = self.__GetAmounts(year)
        self.__PrintHeader(outFile, year)
        deductibleInfo = self.__PrintAmounts(outFile,
                "Deductible Causes", amounts, deductible = True)
        notDeductibleInfo = self.__PrintAmounts(outFile,
                "Not Deductible Causes", amounts, deductible = False)
        donations, looseCash = zip(deductibleInfo, notDeductibleInfo)
        self.__PrintFooter(outFile, sum(donations), sum(looseCash))

