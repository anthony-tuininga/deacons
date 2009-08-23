"""
Print a report of the cheques written for a particular deposit, providing the
details of the which amounts were taken from each collection.
"""

import ceGUI
import Common
import wx

class Report(ceGUI.Report):
    title = "Cheques for Deposit"


class ReportBody(Common.ReportBody):

    def __init__(self):
        super(ReportBody, self).__init__()
        self.font = wx.Font(42, wx.SWISS, wx.NORMAL, wx.NORMAL)
        self.boldFont = wx.Font(42, wx.SWISS, wx.NORMAL, wx.BOLD)

    def Retrieve(self, depositId, dateDeposited):

        # keep the deposit date for printing in the header of the report
        self.dateDeposited = dateDeposited

        # retrieve the cheques for the report
        cursor = self.cache.connection.cursor()
        cursor.execute("""
                select
                  cq.ChequeId,
                  cq.ChequeNumber,
                  ( select Description
                    from Causes
                    where CauseId = cq.CauseId
                  ),
                  ( select sum(ca.ChequeAmount + ca.CashAmount)
                    from
                      CollectionAmounts ca,
                      ChequeAmounts cqa
                    where cqa.ChequeId = cq.ChequeId
                      and ca.CollectionId = cqa.CollectionId
                      and ca.CauseId = cqa.CauseId
                  )
                from Cheques cq
                where ChequeId in
                    ( select ca.ChequeId
                      from
                        ChequeAmounts ca,
                        Collections c
                      where c.DepositId = ?
                        and ca.CollectionId = c.CollectionId
                    )
                order by cq.ChequeNumber""",
                depositId)
        self.cheques = cursor.fetchall()

        # retrieve the cheque amounts
        numLines = len(self.cheques) * 2
        cursor.execute("""
                select
                  cqa.ChequeId,
                  ct.DateCollected,
                  ca.ChequeAmount + ca.CashAmount
                from
                  CollectionAmounts ca,
                  Collections ct,
                  ChequeAmounts cqa
                where ct.CollectionId = ca.CollectionId
                  and ca.CollectionId = cqa.CollectionId
                  and ca.CauseId = cqa.CauseId
                  and cqa.ChequeId in
                    ( select cqa.ChequeId
                      from
                        ChequeAmounts ca,
                        Collections c
                      where c.DepositId = ?
                        and ca.CollectionId = c.CollectionId
                    )""",
                depositId)
        self.amounts = {}
        for chequeId, date, amount in cursor:
            numLines += 1
            amounts = self.amounts.get(chequeId)
            if amounts is None:
                amounts = self.amounts[chequeId] = []
            amounts.append((date, amount))

    def OnPrintPage(self, dc, pageNum):
        dc.SetFont(self.font)
        title = "Cheques Written on %s" % \
                self.dateDeposited.strftime("%A, %B %d, %Y")
        self.DrawTextCenteredOnPage(dc, title, 120)
        y = 300
        pointsPerLine = 42
        grandTotal = 0.0
        for chequeId, chequeNumber, causeDescription, totalAmount \
                in self.cheques:
            dc.DrawText(str(chequeNumber), 300, y)
            dc.DrawText(causeDescription, 400, y)
            y += pointsPerLine
            for date, amount in self.amounts[chequeId]:
                dc.DrawText(date.strftime("%A, %B %d, %Y"), 400, y)
                self.DrawTextRightJustified(dc, Common.FormattedAmount(amount),
                        1500, y)
                y += pointsPerLine
            dc.SetFont(self.boldFont)
            self.DrawTextRightJustified(dc,
                    Common.FormattedAmount(totalAmount), 1500, y)
            grandTotal += totalAmount
            dc.SetFont(self.font)
            y += pointsPerLine
        y += pointsPerLine
        dc.SetFont(self.boldFont)
        self.DrawTextRightJustified(dc, Common.FormattedAmount(grandTotal),
                1500, y)
        return True
