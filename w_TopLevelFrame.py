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
        self.AddMenuItem(menu, "&Elders", "Edit elders",
                windowName = "w_Elders.EditWindow")
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

    def OnCreateMenus(self):
        self.__CreateFileMenu()
        self.__CreateEditMenu()
        self.__CreateHelpMenu()

    def OnCreateToolbar(self):
        self.AddToolbarItem("Exit", wx.ART_QUIT,
                shortHelp = "Exit the application",
                longHelp = "Exit the application.",
                method = self.OnExit)

