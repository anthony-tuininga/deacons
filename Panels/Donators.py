"""
Panel which displays donators and enables editing of them.
"""

import ceGUI
import Models

class Panel(ceGUI.DataListPanel):
    editDialogName = "EditDialogs.Donators.Dialog"

    def OnCreateFilterArgs(self):
        ceGUI.FilterArgStr(self, "lastName", "Last Name:", size = (150, -1))
        ceGUI.FilterArgStr(self, "givenNames", "Given Names:",
                size = (150, -1))


class List(ceGUI.DataList):

    def OnCreate(self):
        self.AddColumn("lastName", "Last Name", 200)
        self.AddColumn("givenNames", "Given Names")


class DataSet(ceGUI.DataSet):
    rowClass = Models.Donators

    def _GetRows(self, lastName, givenNames):
        rows = self.config.GetCachedRows(self.rowClass)
        if lastName is not None:
            rows = [r for r in rows if lastName in r.lastName.upper()]
        if givenNames is not None:
            rows = [r for r in rows if r.givenNames is not None \
                    and givenNames in r.givenNames.upper()]
        return rows

