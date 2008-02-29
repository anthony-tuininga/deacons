"""
Print tax receipts.
"""

import wx

import Cache
import Common
import Reports

class Report(Reports.ReportWithPreview):
    title = "Tax Receipts"


class ReportBody(Reports.ReportBody):

    def _OnInitialize(self):
        self.normalFont = wx.Font(40, wx.SWISS, wx.NORMAL, wx.NORMAL)
        self.italicFont = wx.Font(40, wx.SWISS, wx.ITALIC, wx.NORMAL)
        self.boldFont = wx.Font(40, wx.SWISS, wx.NORMAL, wx.BOLD)
        self.receiptsPerPage = 3
        self.leftMargin_1 = 150
        self.leftMargin_2 = 1250
        self.pointsPerLine = 51

    def Retrieve(self, year, receipts):

        # retrieve all of the receipts for the year
        cursor = self.connection.cursor()
        cursor.execute("""
                select
                  r.ReceiptNumber,
                  r.DonatorId,
                  r.Amount,
                  r.DateIssued,
                  r.IsDuplicate,
                  ( select AssignedNumber
                    from DonatorsForYear
                    where DonatorId = r.DonatorId
                      and Year = r.Year
                  )
                from TaxReceipts r
                where r.Year = ?""",
                year)
        rows = {}
        for receiptNumber, donatorId, amount, dateIssued, isDup, \
                assignedNumber in cursor:
            rows[receiptNumber] = (receiptNumber, donatorId, amount, \
                    dateIssued, isDup, assignedNumber)

        # determine the data that needs to be printed
        self.year = year
        self.data = [rows[r.receiptNumber] for r in receipts]

        # set the number of pages to print
        numPages = len(self.data) / self.receiptsPerPage
        if len(self.data) % self.receiptsPerPage:
            numPages += 1
        self.SetMaxPage(numPages)

    def DrawField(self, dc, label, value, x, y):
        label += ": "
        dc.SetFont(self.italicFont)
        labelWidth, labelHeight = dc.GetTextExtent(label)
        dc.DrawText(label, x, y)
        dc.SetFont(self.normalFont)
        dc.DrawText(value, x + labelWidth, y)

    def OnPrintPage(self, pageNum):

        # initialize
        dc = self.GetDC()
        startPos = (pageNum - 1) * self.receiptsPerPage
        data = self.data[startPos:startPos + self.receiptsPerPage]

        # print each label
        topMargin = 140
        for receiptNumber, donatorId, amount, dateIssued, isDup, \
                assignedNumber in data:

            # determine name and address of the donator
            donator = self.cache.DonatorForId(donatorId)
            name = donator.name
            address = donator.address or "UNKNOWN"

            # set the value for the receipt number field
            receiptNumber = str(receiptNumber)
            if isDup:
                receiptNumber += " (DUPLICATE)"

            # print the name and address of the church
            dc.SetFont(self.boldFont)
            dc.DrawText("Orthodox Reformed Church of Edmonton",
                    self.leftMargin_1, topMargin + self.pointsPerLine * 0)
            dc.SetFont(self.normalFont)
            dc.DrawText("11610 - 95A Street NW",
                    self.leftMargin_1, topMargin + self.pointsPerLine * 1)
            dc.DrawText("Edmonton, AB",
                    self.leftMargin_1, topMargin + self.pointsPerLine * 2)
            dc.DrawText("T5G 1P8",
                    self.leftMargin_1, topMargin + self.pointsPerLine * 3)

            # print the name and address from whom the donation was received
            dc.SetFont(self.italicFont)
            dc.DrawText("Received From:",
                    self.leftMargin_1, topMargin + self.pointsPerLine * 5)
            dc.SetFont(self.normalFont)
            dc.DrawText(name,
                    self.leftMargin_1, topMargin + self.pointsPerLine * 7)
            index = 7
            for addressLine in address.splitlines():
                index += 1
                dc.DrawText(addressLine, self.leftMargin_1,
                        topMargin + self.pointsPerLine * index)

            # print the header for the second column
            dc.SetFont(self.boldFont)
            dc.DrawText("OFFICIAL RECEIPT for",
                    self.leftMargin_2, topMargin + self.pointsPerLine * 0)
            dc.DrawText("INCOME TAX PURPOSES",
                    self.leftMargin_2, topMargin + self.pointsPerLine * 1)
            dc.SetFont(self.normalFont)
            dc.DrawText("Charitable Reg. #89329-2060-RR001",
                    self.leftMargin_2, topMargin + self.pointsPerLine * 2)
            self.DrawField(dc, "Year", str(self.year),
                    self.leftMargin_2, topMargin + self.pointsPerLine * 4)
            self.DrawField(dc, "Envelope Number", str(assignedNumber),
                    self.leftMargin_2, topMargin + self.pointsPerLine * 5)
            self.DrawField(dc, "Receipt Number", receiptNumber,
                    self.leftMargin_2, topMargin + self.pointsPerLine * 6)
            self.DrawField(dc, "Date Issued",
                    dateIssued.strftime("%B %d, %Y"),
                    self.leftMargin_2, topMargin + self.pointsPerLine * 7)
            self.DrawField(dc, "Amount", Common.FormattedAmount(amount),
                    self.leftMargin_2, topMargin + self.pointsPerLine * 8)
            dc.DrawText("PER: " + "_" * 25,
                    self.leftMargin_2, topMargin + self.pointsPerLine * 10)

            # skip to the next location
            topMargin += 930

        return True

