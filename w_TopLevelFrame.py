"""
Top level frame for the application.
"""

import ceGUI
import cx_Logging
import wx

from wx.lib.flatnotebook import FlatNotebook

class Frame(ceGUI.TopLevelFrame):
    title = "Deacons"

    def __AddDepositPage(self, depositId, dateDeposited):
        text = dateDeposited.strftime("Deposit - %A, %B %d, %Y")
        page = self.__AddPage("w_Deposits.Panel", text)
        page.Retrieve(depositId, dateDeposited)
        return page

    def __AddPage(self, name, text):
        currentPage = self.notebook.GetCurrentPage()
        newPage = ceGUI.OpenWindow(name, self.notebook, instanceName = text)
        if newPage is currentPage:
            return newPage
        if currentPage is not None:
            currentPage.SaveSettings()
        for pageIndex in range(self.notebook.GetPageCount()):
            page = self.notebook.GetPage(pageIndex)
            if newPage is page:
                self.notebook.SetSelection(pageIndex)
                return newPage
        self.notebook.AddPage(newPage, text)
        newPage.RestoreSettings()
        return newPage

    def __CreateEditMenu(self):
        menu = self.AddMenu("&Edit")
        self.AddMenuItem(menu, "&Preferences", "Edit preferences",
                self.OnEditPreferences)

    def __CreateFileMenu(self):
        menu = self.AddMenu("&File")
        self.AddMenuItem(menu, "&New", "New deposit", method = self.OnNew)
        self.AddMenuItem(menu, "&Open", "Open deposit", method = self.OnOpen)
        menu.AddSeparator()
        self.AddMenuItem(menu, "&Elders", "Edit elders",
                method = self.OnEditElders, passEvent = False)
        self.AddMenuItem(menu, "&Causes", "Edit causes",
                method = self.OnEditCauses, passEvent = False)
        self.AddMenuItem(menu, "&Donators", "Edit donators",
                method = self.OnEditDonators, passEvent = False)
        self.AddMenuItem(menu, "&Years", "Edit years",
                method = self.OnEditYears, passEvent = False)
        menu.AddSeparator()
        self.AddStockMenuItem(menu, wx.ID_EXIT, self.OnExit)

    def __CreateHelpMenu(self):
        menu = self.AddMenu("&Help")
        self.AddStockMenuItem(menu, wx.ID_ABOUT, self.OnAbout)

    def __CreateReportsMenu(self):
        menu = self.AddMenu("&Reports")
        self.AddMenuItem(menu, "Monthly Report", "Monthly Report",
                method = self.OnMonthlyReport, passEvent = False)
        self.AddMenuItem(menu, "Quarterly Report", "Quarterly Report",
                method = self.OnQuarterlyReport, passEvent = False)
        self.AddMenuItem(menu, "Yearly Report", "Yearly Report",
                method = self.OnYearlyReport, passEvent = False)

    def __PrintReport(self, name):
        cls = ceGUI.GetModuleItem(name, "Report")
        self.SetStatusBarText("Printing report...")
        busyCursor = wx.BusyCursor()
        try:
            report = cls(self.cache)
            report.Print(self)
            self.SetStatusBarText("Report printed successfully.")
        except:
            cx_Logging.LogException("report failed")
            self.SetStatusBarText("Report failed.")

    def _AddCausesForYearPage(self, year):
        text = "%s - Causes" % year
        page = self.__AddPage("w_CausesForYear.Panel", text)
        page.list.Retrieve(year)

    def _AddDonatorsForYearPage(self, year):
        text = "%s - Donators" % year
        page = self.__AddPage("w_DonatorsForYear.Panel", text)
        page.Setup(year)

    def _AddTaxReceiptsPage(self, year):
        text = "%s - Tax Receipts" % year
        page = self.__AddPage("w_TaxReceipts.Panel", text)
        page.list.Retrieve(year)

    def OnCreate(self):
        self.notebook = FlatNotebook(self,
                style = wx.lib.flatnotebook.FNB_NO_NAV_BUTTONS | \
                        wx.lib.flatnotebook.FNB_NO_X_BUTTON | \
                        wx.lib.flatnotebook.FNB_X_ON_TAB)
        self.BindEvent(self.notebook,
                wx.lib.flatnotebook.EVT_FLATNOTEBOOK_PAGE_CLOSING,
                self.OnPageClosing, skipEvent = False)
        self.statusBar = wx.StatusBar(self)
        self.SetStatusBar(self.statusBar)

    def OnCreateMenus(self):
        self.__CreateFileMenu()
        self.__CreateEditMenu()
        self.__CreateReportsMenu()
        self.__CreateHelpMenu()

    def OnCreateToolbar(self):
        self.AddToolbarItem("New", wx.ART_NEW,
                shortHelp = "New deposit",
                longHelp = "Create new deposit.",
                method = self.OnNew)
        self.AddToolbarItem("Open", wx.ART_FILE_OPEN,
                shortHelp = "Open deposit",
                longHelp = "Open deposit created earlier.",
                method = self.OnOpen)
        self.toolbar.AddSeparator()
        self.AddToolbarItem("Exit", wx.ART_QUIT,
                shortHelp = "Exit the application",
                longHelp = "Exit the application.",
                method = self.OnExit)

    def OnEditCauses(self):
        self.__AddPage("w_Causes.Panel", "Causes")

    def OnEditDonators(self):
        self.__AddPage("w_Donators.Panel", "Donators")

    def OnEditElders(self):
        self.__AddPage("w_Elders.Panel", "Elders")

    def OnEditYears(self):
        self.__AddPage("w_Years.Panel", "Years")

    def OnExit(self, event):
        for pageIndex in range(self.notebook.GetPageCount()):
            page = self.notebook.GetPage(pageIndex)
            page.SaveSettings()
        super(Frame, self).OnExit(event)

    def OnMonthlyReport(self):
        self.__PrintReport("ReportDefs.Monthly")

    def OnNew(self, event):
        dialog = self.OpenWindow("SelectDialogs.Date.Dialog")
        if dialog.ShowModal() == wx.ID_OK:
            dateDeposited = dialog.GetDate()
            cursor = self.config.connection.cursor()
            cursor.execute("select nextval('DepositId_s')::integer")
            depositId, = cursor.fetchone()
            cursor.execute("""
                        insert into Deposits (DepositId, DateDeposited)
                        values (?, ?)""",
                        depositId, dateDeposited)
            self.config.connection.commit()
            self.__AddDepositPage(depositId, dateDeposited)
        dialog.Destroy()

    def OnOpen(self, event):
        dialog = self.OpenWindow("SelectDialogs.Deposit.Dialog")
        if dialog.ShowModal() == wx.ID_OK:
            depositInfo = dialog.GetSelectedItem()
            self.__AddDepositPage(depositInfo.depositId,
                    depositInfo.dateDeposited)
        dialog.Destroy()

    def OnPageClosing(self, event):
        page = self.notebook.GetCurrentPage()
        if not page.ContinueQuery():
            event.Veto()
        else:
            page.SaveSettings()
            event.Skip()

    def OnQuarterlyReport(self):
        self.__PrintReport("ReportDefs.Quarterly")

    def OnYearlyReport(self):
        self.__PrintReport("ReportDefs.Yearly")

    def SetStatusBarText(self, message):
        self.statusBar.SetStatusText(message)

