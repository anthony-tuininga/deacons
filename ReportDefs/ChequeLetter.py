"""
Print the letter sent to the causes along with a cheque.
"""

import ceGUI
import Common
import datetime
import wx
import os
import sys

class Report(ceGUI.Report):
    title = "Cover Letter for Cheque"


class ReportBody(Common.ReportBody):

    def OnCreate(self):
        self.bodyFont = wx.Font(30, wx.SWISS, wx.NORMAL, wx.NORMAL)
        self.headerFont = wx.Font(42, wx.SWISS, wx.NORMAL, wx.BOLD)

    def OnPrintPage(self, dc, pageNum):
        dc.SetFont(self.headerFont)
        self.DrawTextCenteredOnPage(dc, "ORTHODOX REFORMED CHURCH OF EDMONTON",
                220)
        dc.SetFont(self.bodyFont)
        self.DrawTextCenteredOnPage(dc,
                "11610 - 95A Street, Edmonton, Alberta T5G 1P8", 280)
        y = 400
        for line in self.lines:
            dc.DrawText(line, 320, y)
            y += 50
        return True

    def Retrieve(self, cheque):
        cause = self.cache.CauseForId(cheque.causeId)
        self.TransformTemplate(cause.address, cheque.amount)

    def TransformTemplate(self, address, amount):
        dirName = os.path.dirname(sys.argv[0])
        fileName = os.path.join(dirName, "CauseLetter.txt")
        value = file(fileName).read()
        value = value.replace("{Date}",
                datetime.date.today().strftime("%B %d, %Y"))
        value = value.replace("{Address}", address)
        value = value.replace("{Amount}", Common.FormattedAmount(amount))
        self.lines = value.splitlines()

