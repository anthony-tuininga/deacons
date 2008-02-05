import ceDatabase
import ceGUI
import wx

import Common

class Panel(ceGUI.DataListPanel):
    editDialogName = "w_YearEdit.Dialog"


class List(ceGUI.DataList):

    def OnCreate(self):
        self.AddColumn("year", "Year", 50)
        self.AddColumn("budgetAmount", "Budget Amount",
                justification = wx.LIST_FORMAT_RIGHT,
                cls = Common.AmountColumn)


class DataSet(ceDatabase.DataSet):
    tableName = "Years"
    attrNames = "year budgetAmount"
    pkAttrNames = "year"

