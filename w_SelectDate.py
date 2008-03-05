"""
Dialog for selecting a date.
"""

import datetime
import ceGUI
import wx.calendar

class Dialog(ceGUI.StandardDialog):
    title = "Select Date"

    def GetDate(self):
        wxDate = self.calendar.GetDate()
        return datetime.date(wxDate.GetYear(), wxDate.GetMonth() + 1,
                wxDate.GetDay())

    def OnCalendarSelected(self, event):
        self.EndModal(wx.ID_OK)
        self.OnOk()

    def OnCreate(self):
        self.calendar = wx.calendar.CalendarCtrl(self, -1, wx.DateTime_Now(),
                style = wx.calendar.CAL_SHOW_HOLIDAYS |
                        wx.calendar.CAL_SUNDAY_FIRST |
                        wx.calendar.CAL_SEQUENTIAL_MONTH_SELECTION)
        self.BindEvent(self.calendar, wx.calendar.EVT_CALENDAR,
                self.OnCalendarSelected)

    def OnLayout(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.calendar, proportion = 1, flag = wx.EXPAND)
        return sizer

    def SetDate(self, date):
        wxDate = wx.DateTimeFromDMY(date.day, date.month - 1, date.year)
        self.calendar.SetDate(wxDate)

