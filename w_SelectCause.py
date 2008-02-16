"""
Dialog for selecting a cause.
"""

import ceDatabase
import ceGUI

class Dialog(ceGUI.SelectionListDialog):
    title = "Select Cause"


class List(ceGUI.List):
    singleSelection = True

    def OnCreate(self):
        self.AddColumn("description", "Description")


class DataSet(ceDatabase.DataSet):

    def _GetRows(self, causes):
        return causes

