"""
Panel displaying the causes for a given year.
"""

import ceDatabase
import ceGUI
import wx

import Common

class Panel(ceGUI.DataListPanel):
    editDialogName = "w_CauseForYearEdit.Dialog"

    def GetEditWindow(self, item = None):
        editWindow = super(Panel, self).GetEditWindow(item)
        if editWindow.dataSet.rows[0].causeId is None:
            editWindow.Destroy()
        else:
            return editWindow


class List(ceGUI.DataList):

    def OnCreate(self):
        self.AddColumn("causeId", "Cause", 150, cls = Common.CauseColumn)
        self.AddColumn("deductible", "Deductible?", cls = Common.BooleanColumn)


class DataSet(ceDatabase.DataSet):
    tableName = "CausesForYear"
    attrNames = "year causeId deductible"
    pkAttrNames = "year causeId"
    retrievalAttrNames = "year"
    charBooleanAttrNames = "deductible"

