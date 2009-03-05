"""
Print a report of the collections and cheques for the deposit which is given
to the treasurer.
"""

import ceGUI

import Common
import Reports

class Report(Reports.ReportWithPreview):
    pass


class PreviewFrame(ceGUI.PreviewFrame):
    title = "Treasurer Summary"


class ReportBody(Reports.ReportBody):
    causeWidth = 530
    amountWidth = 230
    bottomMargin = 2670
    topMargin = 125
    leftMargin = 355
    separationPoints = 50
    headerHeight = 125

    def _GetBoxHeight(self, numCauses):
        return self.BoxedHeight(2) + self.BoxedHeight(numCauses) + \
            self.BoxedHeight(1)

    def OnPrintPage(self, pageNum):
        dc = self.GetDC()
        dc.SetFont(self.font)
        y = self.topMargin
        for dateCollected, causes in self.pageData[pageNum - 1]:
            y = self.PrintHeader(dc, dateCollected, y)
            y = self.PrintCauses(dc, causes, y)
        return True

    def PrintAmounts(self, dc, y, cheques, envelopeCash, looseCash):
        x = self.leftMargin + self.causeWidth + self.amountWidth - \
                self.interColumnWidth
        self.DrawTextRightJustified(dc, x, y, Common.FormattedAmount(cheques))
        x += self.amountWidth
        self.DrawTextRightJustified(dc, x, y,
                Common.FormattedAmount(envelopeCash))
        x += self.amountWidth
        self.DrawTextRightJustified(dc, x, y,
                Common.FormattedAmount(looseCash))
        x += self.amountWidth
        self.DrawTextRightJustified(dc, x, y,
                Common.FormattedAmount(cheques + envelopeCash + looseCash))

    def PrintHeader(self, dc, dateCollected, y):
        self.CenterOnPage(dc, y, "Treasurer Summary")
        self.CenterOnPage(dc, y + self.pointsPerLine,
                dateCollected.strftime("%A, %B %d, %Y"))
        return y + self.headerHeight

    def PrintCauses(self, dc, amounts, y):

        # determine the width and height of the box
        height = self._GetBoxHeight(len(amounts))
        width = self.causeWidth + 4 * self.amountWidth

        # set up an array for the widths and titles
        columns = [
                ( self.causeWidth, "", "Cause" ),
                ( self.amountWidth, "", "Cheques" ),
                ( self.amountWidth, "Envelope", "Cash" ),
                ( self.amountWidth, "Loose", "Cash" ),
                ( self.amountWidth, "", "Total" )
        ]

        # draw the lines and titles for the columns
        for tempY in (y, y + self.BoxedHeight(2),
                y + height - self.BoxedHeight(1), y + height):
            dc.DrawLine(self.leftMargin, tempY, self.leftMargin + width, tempY)
        x = self.leftMargin
        for points, title_1, title_2 in columns:
            dc.DrawLine(x, y, x, y + height)
            if title_1:
                self.DrawTextCentred(dc, x + points / 2, y + self.borderHeight,
                        title_1)
            self.DrawTextCentred(dc, x + points / 2,
                    y + self.borderHeight + self.pointsPerLine, title_2)
            x += points
        dc.DrawLine(self.leftMargin + width, y,
            self.leftMargin + width, y + height)

        # draw the cause lines
        chequeTotal = envelopeCashTotal = looseCashTotal = 0.0
        tempY = y + self.BoxedHeight(2) + self.borderHeight
        for cause, cheques, envelopeCash, looseCash in amounts:
            chequeTotal += cheques
            envelopeCashTotal += envelopeCash
            looseCashTotal += looseCash
            x = self.leftMargin + self.interColumnWidth
            dc.DrawText(cause, x, tempY)
            self.PrintAmounts(dc, tempY, cheques, envelopeCash, looseCash)
            tempY += self.pointsPerLine

        # draw the totals for the collection
        self.PrintAmounts(dc, tempY + self.borderHeight + self.borderHeight,
                chequeTotal, envelopeCashTotal, looseCashTotal)

        # return the bottom y coordinate
        return y + height + self.separationPoints

    def Retrieve(self, depositId):

        # retrieve the set of dates collected for the deposit
        cursor = self.connection.cursor()
        cursor.execute("""
                select distinct DateCollected
                from Collections
                where DepositId = ?
                order by DateCollected""",
                depositId)
        datesCollected = [d for d, in cursor]
        causesForDate = dict((d, []) for d in datesCollected)

        # retrieve the cause rows for the deposit
        cursor.execute("""
                select
                    ct.DateCollected,
                    c.Description,
                    sum(ca.ChequeAmount),
                    sum(ca.EnvelopeCash),
                    sum(ca.CashAmount - ca.EnvelopeCash)
                from
                    Collections ct
                    join CollectionAmounts ca
                        on ca.CollectionId = ct.CollectionId
                    join Causes c
                        on c.CauseId = ca.CauseId
                where ct.DepositId = ?
                group by
                    ct.DateCollected,
                    c.CauseId,
                    c.Description
                order by
                    ct.DateCollected,
                    case when c.CauseId = 1 then 0 else 1 end,
                    c.Description""",
                depositId)
        for dateCollected, cause, cheques, envelopeCash, looseCash in cursor:
            info = (cause, cheques, envelopeCash, looseCash)
            causesForDate[dateCollected].append(info)

        # calculate the number of pages to use
        y = self.topMargin
        self.pageData = []
        datesForPage = []
        for dateCollected in datesCollected:
            causes = causesForDate[dateCollected]
            size = self.headerHeight + self._GetBoxHeight(len(causes))
            if y + size > self.bottomMargin:
                self.pageData.append(datesForPage)
                datesForPage = []
                y = self.topMargin
            datesForPage.append((dateCollected, causes))
            y += size + self.separationPoints
        self.pageData.append(datesForPage)
        self.SetMaxPage(len(self.pageData))

