"""
Panel displaying the donators for a given year and their assigned numbers.
"""

import ceDatabase
import ceGUI
import wx

import Common

class Panel(ceGUI.DataListPanel):
    editDialogName = "w_DonatorForYearEdit.Dialog"

    def GetEditWindow(self, item = None):
        editWindow = super(Panel, self).GetEditWindow(item)
        if editWindow.dataSet.rows[0].donatorId is None:
            editWindow.Destroy()
        else:
            return editWindow


class List(ceGUI.DataList):

    def OnCreate(self):
        self.AddColumn("assignedNumber", "Number", 75,
                justification = wx.LIST_FORMAT_RIGHT)
        self.AddColumn("lastName", "Last Name", 200,
                cls = Common.LastNameColumn)
        self.AddColumn("givenNames", "Given Names",
                cls = Common.GivenNamesColumn)


class DataSet(ceDatabase.DataSet):
    tableName = "DonatorsForYear"
    attrNames = "year donatorId assignedNumber"
    pkAttrNames = "year donatorId"
    retrievalAttrNames = "year"

