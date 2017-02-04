"""
Panel which displays causes and enables editing of them.
"""

import ceGUI
import Models

class Panel(ceGUI.DataListPanel):
    editDialogName = "EditDialogs.Causes.Dialog"


class List(ceGUI.DataList):

    def OnCreate(self):
        self.AddColumn("description", "Description")


class DataSet(ceGUI.DataSet):
    rowClass = Models.Causes

