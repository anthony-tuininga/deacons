import ceGUI
import wx

from wx.lib.flatnotebook import FlatNotebook

class Frame(ceGUI.TopLevelFrame):
    title = "Deacons"

    def __AddDepositPage(self, depositId, dateDeposited):
        text = dateDeposited.strftime("%a, %b %d/%y")
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
        self.AddMenuItem(menu, "&Elders", "Edit elders",
                method = self.OnEditElders, passEvent = False)
        self.AddMenuItem(menu, "&Causes", "Edit causes",
                windowName = "w_Causes.EditWindow")
        self.AddMenuItem(menu, "De&posits", "Edit deposits",
                windowName = "w_Deposits.EditWindow")
        self.AddMenuItem(menu, "&Donators", "Edit donators",
                windowName = "w_Donators.EditWindow")
        self.AddMenuItem(menu, "&Years", "Edit years",
                windowName = "w_Years.EditWindow")
        menu.AppendSeparator()
        self.AddStockMenuItem(menu, wx.ID_EXIT, self.OnExit)

    def __CreateHelpMenu(self):
        menu = self.AddMenu("&Help")
        self.AddStockMenuItem(menu, wx.ID_ABOUT, self.OnAbout)

    def OnCreate(self):
        self.notebook = FlatNotebook(self,
                style = wx.lib.flatnotebook.FNB_NO_NAV_BUTTONS | \
                        wx.lib.flatnotebook.FNB_NO_X_BUTTON | \
                        wx.lib.flatnotebook.FNB_X_ON_TAB)
        self.BindEvent(self.notebook,
                wx.lib.flatnotebook.EVT_FLATNOTEBOOK_PAGE_CLOSING,
                self.OnPageClosing, skipEvent = False)

    def OnCreateMenus(self):
        self.__CreateFileMenu()
        self.__CreateEditMenu()
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

    def OnEditElders(self):
        self.__AddPage("w_Elders.Panel", "Elders")

    def OnExit(self, event):
        for pageIndex in range(self.notebook.GetPageCount()):
            page = self.notebook.GetPage(pageIndex)
            page.SaveSettings()
        super(Frame, self).OnExit(event)

    def OnNew(self, event):
        pass

    def OnOpen(self, event):
        dialog = self.OpenWindow("w_SelectDeposit.Dialog")
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

