"""
Print a report of the cheques, coin and cash deposited.
"""

import Common
import Reports

class Report(Reports.ReportWithPreview):
    title = "Deposit Summary"

    def _GetPrintArgs(self):
        return self.parentWindow.depositId, self.parentWindow.dateDeposited


class ReportBody(Reports.ReportBody):
    chequeColumns = 8
    chequeColumnWidth = 230
    cashColumnWidth = 530

    def OnPrintPage(self, pageNum):

        # initialize some constants
        topMargin = 120
        leftMargin = 170
        interBoxWidth = 100

        # print the header
        dc = self.GetDC()
        dc.SetFont(self.font)
        self.CenterOnPage(dc, topMargin,
                "Orthodox Reformed Church of Edmonton")
        self.CenterOnPage(dc, topMargin + self.pointsPerLine,
                self.depositDate.strftime("%A, %B %d, %Y"))
        self.CenterOnPage(dc, topMargin + self.pointsPerLine * 2,
                "For Account 72926")

        # print the rest of the report
        y, chequeTotal = self.PrintChequesTable(dc, leftMargin,
                topMargin + 200)
        coinTotal = self.PrintCashTable(dc, "Coin", self.coin, leftMargin,
                y + interBoxWidth)
        cashTotal = self.PrintCashTable(dc, "Cash", self.cash,
                leftMargin + self.cashColumnWidth + interBoxWidth,
                y + interBoxWidth)
        self.PrintGrandTotal(dc, chequeTotal + coinTotal + cashTotal,
                leftMargin + self.cashColumnWidth * 2 + interBoxWidth * 2,
                y + interBoxWidth + 140)
        return True

    def PrintCashTable(self, dc, title, entries, startX, startY):

        # determine the width and height of the box
        width = self.cashColumnWidth
        numRows = len(entries)
        boxedHeight = self.BoxedHeight(1)
        height = boxedHeight + self.BoxedHeight(numRows) + boxedHeight

        # draw the lines
        for y in (startY, startY + boxedHeight, startY + height - boxedHeight,
                startY + height):
            dc.DrawLine(startX, y, startX + width, y)
        for x in (startX, startX + width):
            dc.DrawLine(x, startY, x, startY + height)

        # draw the title
        self.DrawTextCentred(dc, startX + width / 2,
                startY + self.borderHeight, title)

        # draw the cash amounts (and acquire grand total)
        grandTotal = 0.0
        y = startY + boxedHeight + self.borderHeight
        for isCoin, value, quantity in entries:
            grandTotal += value * quantity
            self.DrawTextRightJustified(dc, startX + 90, y, str(int(quantity)))
            dc.DrawText("x", startX + 100, y)
            self.DrawTextRightJustified(dc, startX + 290, y,
                    Common.FormattedAmount(value))
            dc.DrawText("=", startX + 300, y)
            self.DrawTextRightJustified(dc,
                    startX + width - self.interColumnWidth, y,
                    Common.FormattedAmount(value * quantity))
            y += self.pointsPerLine

        # draw the grand total
        x = startX + width - self.interColumnWidth
        y = startY + height - boxedHeight + self.borderHeight
        self.DrawTextRightJustified(dc, x, y,
                "Total:  %s" % Common.FormattedAmount(grandTotal))
        return grandTotal

    def PrintChequesTable(self, dc, startX, startY):

        # determine the width and height of the box
        width = self.chequeColumns * self.chequeColumnWidth
        numRows = len(self.cheques) / self.chequeColumns
        if len(self.cheques) % self.chequeColumns != 0:
            numRows += 1
        boxedHeight = self.BoxedHeight(1)
        height = boxedHeight + self.BoxedHeight(numRows) + boxedHeight

        # draw the lines
        for y in (startY, startY + boxedHeight, startY + height - boxedHeight,
                startY + height):
            dc.DrawLine(startX, y, startX + width, y)
        for x in (startX, startX + width):
            dc.DrawLine(x, startY, x, startY + height)
        topY = startY + boxedHeight
        bottomY = startY + height - boxedHeight
        for i in range(self.chequeColumns):
            x = startX + self.chequeColumnWidth * (i + 1)
            dc.DrawLine(x, topY, x, bottomY)

        # draw the title
        self.DrawTextCentred(dc, startX + width / 2,
                startY + self.borderHeight, "Cheques")

        # draw the cheque amounts (and acquire grand total)
        grandTotal = 0.0
        x = startX + self.chequeColumnWidth - self.interColumnWidth
        y = topY = startY + boxedHeight + self.borderHeight
        for rowNum, amount in enumerate(self.cheques):
            if rowNum > 0 and rowNum % numRows == 0:
                x += self.chequeColumnWidth
                y = topY
            self.DrawTextRightJustified(dc, x, y,
                    Common.FormattedAmount(amount))
            grandTotal += amount
            y += self.pointsPerLine

        # draw the grand total (amount and number of cheques)
        y = startY + height - self.pointsPerLine - self.borderHeight
        text = "Number of Cheques: %d" % len(self.cheques)
        dc.DrawText(text, startX + 50, y)
        x = startX + width - self.interColumnWidth
        text = "Total:  %s" % Common.FormattedAmount(grandTotal)
        self.DrawTextRightJustified(dc, x, y, text)

        # set up the top margin for the next section
        return startY + height, grandTotal

    def PrintGrandTotal(self, dc, grandTotal, startX, startY):

        # determine the width and height of the box
        width = self.cashColumnWidth
        boxedHeight = self.BoxedHeight(1)
        height = boxedHeight * 2

        # draw the lines
        for y in (startY, startY + boxedHeight, startY + height - boxedHeight,
                startY + height):
            dc.DrawLine(startX, y, startX + width, y)
        for x in (startX, startX + width):
            dc.DrawLine(x, startY, x, startY + height)

        # draw the text
        self.DrawTextCentred(dc, startX + width / 2, startY + self.borderHeight,
                "TOTAL DEPOSIT")
        self.DrawTextCentred(dc, startX + width / 2,
                startY + boxedHeight + self.borderHeight,
                Common.FormattedAmount(grandTotal))

    def Retrieve(self, depositId, depositDate):

        # keep the deposit date for printing in the header of the report
        self.depositDate = depositDate

        # retrieve the cheques for the deposit
        cursor = self.connection.cursor()
        cursor.execute("""
                select sum(d.Amount)
                from
                  Donations d,
                  SplitDonations sd,
                  Collections c
                where c.DepositId = ?
                  and sd.CollectionId = c.CollectionId
                  and d.SplitDonationId = sd.SplitDonationId
                group by d.SplitDonationId
              union all
                select d.Amount
                from
                  Donations d,
                  Collections c
                where c.DepositId = ?
                  and d.CollectionId = c.CollectionId
                  and d.Cash = 'f'
                  and d.SplitDonationId is null""",
                depositId, depositId)
        self.cheques = [r for r, in cursor]

        # retrieve the coin/cash for the deposit
        cursor.execute("""
                select
                  cd.Coin,
                  cd.Value,
                  ( select cast(coalesce(sum(cc.Quantity), 0) as integer)
                    from
                      CollectionCash cc,
                      Collections c
                    where c.DepositId = ?
                      and cc.CollectionId = c.CollectionId
                      and cc.CashDenominationId = cd.CashDenominationId
                  )
                from CashDenominations cd
                order by cd.Value""",
                depositId)
        cash = cursor.fetchall()
        self.coin = [r for r in cash if int(r[0])]
        self.cash = [r for r in cash if not int(r[0])]

        # always one page
        self.SetMaxPage(1)

