"""
Dialog for selecting a year.
"""

import ceGUI

import Models

class Dialog(ceGUI.SelectionListDialog):
    title = "Select Year"
    defaultSize = (235, 320)

    def OnCreate(self):
        super(Dialog, self).OnCreate()
        self.Retrieve()


class List(ceGUI.List):
    singleSelection = True
    sortOnRetrieve = False

    def OnCreate(self):
        self.AddColumn("year", "Year")


class DataSet(ceGUI.DataSet):
    rowClass = Models.Years

