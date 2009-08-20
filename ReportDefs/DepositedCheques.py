"""
Print a report of the cheques deposited with the name of the person to whom
the cheque is attributed.
"""

import ceGUI
import Common

class Report(ceGUI.Report):
    title = "Deposited Cheques"


class ReportBody(Common.ReportBody):
    nameColumnWidth = 675
    amountColumnWidth = 230
    columnWidth = nameColumnWidth + amountColumnWidth
    numColumns = 2
    numChequesPerColumn = 55
    numChequesPerPage = numColumns * numChequesPerColumn

    def GetNumberOfPages(self, dc):
        numPages, leftOver = divmod(len(self.cheques), self.numChequesPerPage)
        if leftOver > 0:
            numPages += 1
        return numPages

    def OnPrintPage(self, dc, pageNum):

        # initialize some constants
        topMargin = 120
        leftMargin = 170

        # print the header
        dc.SetFont(self.font)
        self.DrawTextCenteredOnPage(dc, "Orthodox Reformed Church of Edmonton",
                topMargin)
        self.DrawTextCenteredOnPage(dc,
                self.depositDate.strftime("%A, %B %d, %Y"),
                topMargin + self.pointsPerLine)
        self.DrawTextCenteredOnPage(dc, "For Account 72926",
                topMargin + self.pointsPerLine * 2)

        # print the rest of the report
        self.PrintChequesTable(dc, pageNum, leftMargin, topMargin + 200)
        return True

    def PrintChequesTable(self, dc, pageNum, startX, startY):

        # determine the width and height of the box
        startIndex = (pageNum - 1) * self.numChequesPerPage
        endIndex = startIndex + self.numChequesPerPage
        cheques = self.cheques[startIndex:endIndex]
        width = self.numColumns * self.columnWidth
        numRows, leftOver = divmod(len(cheques), self.numColumns)
        if leftOver > 0:
            numRows += 1
        boxedHeight = self.BoxedHeight(1)
        height = boxedHeight + self.BoxedHeight(numRows)

        # draw the lines and headers
        for y in (startY, startY + boxedHeight, startY + height):
            dc.DrawLine(startX, y, startX + width, y)
        for i in range(self.numColumns):
            x = startX + self.columnWidth * i
            dc.DrawLine(x, startY, x, startY + height)
            dc.DrawLine(x + self.nameColumnWidth, startY,
                    x + self.nameColumnWidth, startY + height)
            self.DrawTextCentered(dc, "Name", x + self.nameColumnWidth / 2,
                    startY + self.borderHeight)
            amountX = x + self.nameColumnWidth + self.amountColumnWidth / 2
            self.DrawTextCentered(dc, "Amount", amountX,
                    startY + self.borderHeight)
        dc.DrawLine(startX + width, startY, startX + width, startY + height)

        # draw the cheque names and amounts
        nameX = startX + self.interColumnWidth
        amountX = startX + self.columnWidth - self.interColumnWidth
        y = topY = startY + boxedHeight + self.borderHeight
        for rowNum, info in enumerate(cheques):
            name, amount = info
            if rowNum > 0 and rowNum % numRows == 0:
                nameX += self.columnWidth
                amountX += self.columnWidth
                y = topY
            dc.DrawText(name, nameX, y)
            self.DrawTextRightJustified(dc, Common.FormattedAmount(amount),
                    amountX, y)
            y += self.pointsPerLine

    def Retrieve(self, depositId, depositDate):

        # keep the deposit date for printing in the header of the report
        self.depositDate = depositDate

        # retrieve the cheques for the deposit
        cursor = self.config.connection.cursor()
        cursor.execute("""
                select min(d.DonatorId), sum(d.Amount)
                from
                  Donations d,
                  SplitDonations sd,
                  Collections c
                where c.DepositId = ?
                  and sd.CollectionId = c.CollectionId
                  and d.SplitDonationId = sd.SplitDonationId
                group by d.SplitDonationId
              union all
                select d.DonatorId, d.Amount
                from
                  Donations d,
                  Collections c
                where c.DepositId = ?
                  and d.CollectionId = c.CollectionId
                  and d.Cash = 'f'
                  and d.SplitDonationId is null""",
                depositId, depositId)
        self.cheques = []
        for donatorId, amount in cursor:
            if donatorId is None:
                name = "Anonymous"
            else:
                donator = self.cache.DonatorForId(donatorId)
                name = donator.reversedName
            self.cheques.append((name, amount))
        self.cheques.sort()

