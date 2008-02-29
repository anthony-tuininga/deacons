"""Defines the base class for printing reports."""

import cx_Logging
import wx

class Report(object):

    def __init__(self, parentWindow):
        self.parentWindow = parentWindow
        self.connection = parentWindow.config.connection
        self.cache = parentWindow.config.cache

    def Print(self):
        args = self._GetPrintArgs()
        if args is None:
            return
        self.parentWindow.SetStatusBarText("Printing report....")
        busyCursor = wx.BusyCursor()
        try:
            self._Print(*args)
            self.parentWindow.SetStatusBarText("Report printed successfully.")
        except:
            cx_Logging.LogException("report failed")
            self.parentWindow.SetStatusBarText("Report failed.")


class ReportWithPreview(Report):

    def __init__(self, parentWindow):
        super(ReportWithPreview, self).__init__(parentWindow)
        bodyClass = __import__(self.__class__.__module__).ReportBody
        self.printout = bodyClass(self.connection, self.cache)
        self.printoutForPrinting = bodyClass(self.connection, self.cache)

    def Print(self, *args):
        busyCursor = wx.BusyCursor()
        self.printout.Retrieve(*args)
        self.printoutForPrinting.Retrieve(*args)
        self.printData = wx.PrintData()
        self.printData.SetPaperId(wx.PAPER_LETTER)
        printData = wx.PrintDialogData(self.printData)
        self.preview = wx.PrintPreview(self.printout, self.printoutForPrinting,
                printData)
        topWindow = wx.GetApp().topWindow
        self.previewFrame = wx.PreviewFrame(self.preview, topWindow,
                self.title, size = (500, 600))
        self.previewFrame.Initialize()
        self.previewFrame.Show(True)


class ReportBody(wx.Printout):

    def __init__(self, connection, cache):
        wx.Printout.__init__(self)
        self.connection = connection
        self.cache = cache
        self.interColumnWidth = 12
        self.borderHeight = 14
        self.pointsPerLine = 42
        self.font = wx.Font(25, wx.ROMAN, wx.NORMAL, wx.NORMAL)
        self._OnInitialize()

    def _OnInitialize(self):
        pass

    def BoxedHeight(self, numRows):
        return self.borderHeight * 2 + self.pointsPerLine * numRows

    def CenterOnPage(self, dc, y, text):
        width, height = dc.GetTextExtent(text)
        x = (self.width - width) / 2
        dc.DrawText(text, x, y)

    def DrawTextCentred(self, dc, x, y, text):
        width, height = dc.GetTextExtent(text)
        dc.DrawText(text, x - width / 2, y)

    def DrawTextRightJustified(self, dc, x, y, text):
        width, height = dc.GetTextExtent(text)
        dc.DrawText(text, x - width, y)

    def GetPageInfo(self):
        return (1, self.maxPage, 1, self.maxPage)

    def HasPage(self, pageNum):
        return (pageNum <= self.maxPage)

    def OnBeginPrinting(self):
        width, height = self.GetPageSizeMM()
        self.width = width * 10
        self.height = height * 10
        self.FitThisSizeToPaper((self.width, self.height))

    def SetMaxPage(self, maxPage = 1):
        self.maxPage = maxPage

