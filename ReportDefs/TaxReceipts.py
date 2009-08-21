"""
Print tax receipts.
"""

import ceGUI
import Common
import wx


class Report(ceGUI.Report):
    title = "Tax Receipts"


class ReportBody(Common.ReportBody):
    receiptsPerPage = 3
    leftMargin_1 = 150
    leftMargin_2 = 1250
    pointsPerLine = 51

    def __init__(self):
        super(ReportBody, self).__init__()
        self.normalFont = wx.Font(40, wx.SWISS, wx.NORMAL, wx.NORMAL)
        self.italicFont = wx.Font(40, wx.SWISS, wx.ITALIC, wx.NORMAL)
        self.boldFont = wx.Font(40, wx.SWISS, wx.NORMAL, wx.BOLD)

    def DrawField(self, dc, label, value, x, y):
        label += ": "
        dc.SetFont(self.italicFont)
        labelWidth, labelHeight = dc.GetTextExtent(label)
        dc.DrawText(label, x, y)
        dc.SetFont(self.normalFont)
        dc.DrawText(value, x + labelWidth, y)

    def GetNumberOfPages(self, dc):
        numPages = len(self.data) / self.receiptsPerPage
        if len(self.data) % self.receiptsPerPage:
            numPages += 1
        return numPages

    def OnPrintPage(self, dc, pageNum):

        # initialize
        startPos = (pageNum - 1) * self.receiptsPerPage
        data = self.data[startPos:startPos + self.receiptsPerPage]

        # print each label
        topMargin = 140
        for receipt in data:

            # determine name and address of the donator
            donator = self.cache.DonatorForId(receipt.donatorId)
            name = donator.name
            address = donator.address or "UNKNOWN"
            assignedNumber = self.cache.AssignedNumberForDonator(donator,
                    self.year)

            # set the value for the receipt number field
            receiptNumber = str(receipt.receiptNumber)
            if receipt.isDuplicate:
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
                    receipt.dateIssued.strftime("%B %d, %Y"),
                    self.leftMargin_2, topMargin + self.pointsPerLine * 7)
            self.DrawField(dc, "Amount",
                    Common.FormattedAmount(receipt.amount), self.leftMargin_2,
                    topMargin + self.pointsPerLine * 8)
            dc.DrawText("PER: " + "_" * 25,
                    self.leftMargin_2, topMargin + self.pointsPerLine * 10)

            # skip to the next location
            topMargin += 930

        return True

    def Retrieve(self, year, receipts):
        self.year = year
        self.data = receipts

