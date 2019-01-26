"""
Top level frame for the application.
"""

import ceGUI
import wx

class Frame(ceGUI.TopLevelFrame):
    title = "Deacons"

    def __CreateEditMenu(self):
        menu = self.AddMenu("&Edit")
        self.AddMenuItem(menu, "&Preferences", "Edit preferences",
                self.OnEditPreferences)

    def __CreateFileMenu(self):
        menu = self.AddMenu("&File")
        self.AddStockMenuItem(menu, wx.ID_EXIT, self.OnExit)

    def __CreateHelpMenu(self):
        menu = self.AddMenu("&Help")
        self.AddStockMenuItem(menu, wx.ID_ABOUT, self.OnAbout)

    def __CreateReportsMenu(self):
        menu = self.AddMenu("&Reports")
        self.AddMenuItem(menu, "&Deposit Summary",
                "Run Deposit Summary Report", self.OnRunDepositSummary,
                createBusyCursor = True, passEvent = False)
        self.AddMenuItem(menu, "&Treasurer Summary",
                "Run Treasurer Summary Report", self.OnRunTreasurerSummary,
                createBusyCursor = True, passEvent = False)

    def OnCreate(self):
        self.topPanel = TopPanel(self)
        self.bottomPanel = BottomPanel(self)
        self.CreateSimpleStatusBar()

    def OnCreateMenus(self):
        self.__CreateFileMenu()
        self.__CreateEditMenu()
        self.__CreateReportsMenu()
        self.__CreateHelpMenu()

    def OnCreateToolbar(self):
        self.insertToolbarItem = self.AddToolbarItem("Insert", wx.ART_NEW,
                shortHelp = "Insert", longHelp = "Insert a new row",
                method = self.OnInsertRow, passEvent = False)
        self.deleteToolbarItem = self.AddToolbarItem("Delete", wx.ART_DELETE,
                shortHelp = "Delete", longHelp = "Delete selected rows",
                method = self.OnDeleteRows, passEvent = False)
        self.toolbar.AddSeparator()
        self.AddToolbarItem("Retrieve", wx.ART_FILE_OPEN,
                shortHelp = "Retrieve",
                longHelp = "Retrieve data from the database",
                method = self.OnRetrieve, passEvent = False)
        self.updateToolbarItem = self.AddToolbarItem("Update",
                wx.ART_FILE_SAVE, shortHelp = "Save changes",
                longHelp = "Save changes to the database",
                method = self.OnUpdate, passEvent = False)
        self.toolbar.AddSeparator()
        self.AddToolbarItem("Exit", wx.ART_QUIT,
                shortHelp = "Exit the application",
                longHelp = "Exit the application.",
                method = self.OnExit)

    def OnDeleteRows(self):
        page = self.bottomPanel.notebook.GetCurrentPage()
        page.DeleteSelectedItems()

    def OnExit(self, event):
        self.topPanel.SaveSettings()
        self.bottomPanel.SaveSettings()
        super(Frame, self).OnExit(event)

    def OnInsertRow(self):
        page = self.bottomPanel.notebook.GetCurrentPage()
        page.InsertItems()

    def OnLayout(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.topPanel, flag = wx.EXPAND)
        sizer.Add(self.bottomPanel, proportion = 1, flag = wx.EXPAND)
        return sizer

    def OnRetrieve(self):
        page = self.bottomPanel.notebook.GetCurrentPage()
        page.Retrieve(refresh = True)

    def OnRunDepositSummary(self):
        self.config.RunReport("DepositSummary")

    def OnRunTreasurerSummary(self):
        self.config.RunReport("TreasurerSummary")

    def OnUpdate(self):
        page = self.bottomPanel.notebook.GetCurrentPage()
        page.UpdateChanges()

    def OnYearChanged(self):
        self.topPanel.OnYearChanged()
        self.bottomPanel.OnYearChanged()


class TopPanel(ceGUI.Panel):

    def OnChangeYear(self):
        self.config.SelectYear()

    def OnCreate(self):
        self.yearLabel = self.AddLabel()
        self.changeButton = self.AddButton("Change...",
                method = self.OnChangeYear, passEvent = False)
        self.OnYearChanged();

    def OnLayout(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.yearLabel, border = 5,
                flag = wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.changeButton, border = 5,
                flag = wx.LEFT | wx.ALIGN_CENTER_VERTICAL)
        return sizer

    def OnYearChanged(self):
        self.yearLabel.SetLabel("Year: %d" % self.config.year)


class BottomPanel(ceGUI.Panel):

    def OnCreate(self):
        self.notebook = ceGUI.Notebook(self)
        self.notebook.AddPage("Panels.Trays.Panel", "Trays")
        self.notebook.AddPage("Panels.Donations.Panel", "Donations")
        self.notebook.AddPage("Panels.Causes.Panel", "Causes")
        self.notebook.AddPage("Panels.Donators.Panel", "Donators")
        self.notebook.AddPage("Panels.TaxReceipts.Panel", "Tax Receipts")
        self.notebook.AddPage("Panels.Years.Panel", "Years")
        self.BindEvent(self.notebook, wx.EVT_NOTEBOOK_PAGE_CHANGED,
                self.OnPageChanged)
        wx.CallAfter(self.OnPageChanged)

    def OnLayout(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.notebook, flag = wx.ALL | wx.EXPAND, border = 5,
                proportion = 1)
        return sizer

    def OnPageChanged(self, event = None):
        if not self:
            return
        obj = event or self.notebook
        selection = obj.GetSelection()
        if selection >= 0:
            page = self.notebook.GetPage(selection)
            page.OnActivated()

    def OnYearChanged(self):
        for page in self.notebook.IterPages():
            page.OnYearChanged()

    def SaveSettings(self):
        self.notebook.SaveSettings()

