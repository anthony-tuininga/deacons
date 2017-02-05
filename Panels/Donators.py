"""
Panel which displays donators and enables editing of them.
"""

import ceGUI
import Models

class Panel(ceGUI.DataListPanel):
    editDialogName = "EditDialogs.Donators.Dialog"


class List(ceGUI.DataList):

    def OnCreate(self):
        self.AddColumn("lastName", "Last Name", 200)
        self.AddColumn("givenNames", "Given Names")


class DataSet(ceGUI.DataSet):
    rowClass = Models.Donators

