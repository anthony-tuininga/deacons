"""
Dialog for selecting a donator.
"""

import ceDatabase
import ceGUI

class Dialog(ceGUI.SelectionListDialog):
    title = "Select Donator"
    defaultSize = (425, 450)


class List(ceGUI.List):
    singleSelection = True

    def OnCreate(self):
        self.AddColumn("lastName", "Last Name", 200)
        self.AddColumn("givenNames", "Given Names")


class DataSet(ceDatabase.DataSet):

    def _GetRows(self, donators):
        return donators

