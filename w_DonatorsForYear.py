"""
Panel displaying the donators for a given year and their assigned numbers.
"""

import ceDatabase
import ceGUI
import wx

import Common
from Cache import Cache

class Panel(ceGUI.DataListPanel):
    editDialogName = "w_DonatorForYearEdit.Dialog"
    updateSubCacheAttrName = "donatorsForYear"

    def GetEditWindow(self, item = None):
        editWindow = super(Panel, self).GetEditWindow(item)
        if editWindow.dataSet.rows[0].donatorId is None:
            editWindow.Destroy()
        else:
            return editWindow

    def Retrieve(self):
        self.list.Retrieve(self.cache, self.year)

    def Setup(self, year):
        self.year = year


class List(ceGUI.DataList):

    def OnCreate(self):
        self.AddColumn("assignedNumber", "Number", 75,
                justification = wx.LIST_FORMAT_RIGHT)
        self.AddColumn("lastName", "Last Name", 200,
                cls = Common.LastNameColumn)
        self.AddColumn("givenNames", "Given Names",
                cls = Common.GivenNamesColumn)

    def OnRefresh(self):
        parent = self.GetParent()
        parent.Retrieve()


class DataSet(ceDatabase.DataSet):
    rowClass = Cache.DonatorsForYearSubCache.rowClass
    tableName = Cache.DonatorsForYearSubCache.rowClass.tableName

    def _GetRows(self, cache, year):
        return cache.DonatorsForYear(year)

