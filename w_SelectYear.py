"""
Dialog for selecting a year.
"""

import ceDatabase
import ceGUI

class Dialog(ceGUI.SelectionListDialog):
    title = "Select Year"

    def OnCreate(self):
        super(Dialog, self).OnCreate()
        self.Retrieve()


class List(ceGUI.List):
    singleSelection = True
    sortOnRetrieve = False

    def OnCreate(self):
        self.AddColumn("year", "Year")


class DataSet(ceDatabase.DataSet):
    tableName = "Years"
    attrNames = "year"
    sortByAttrNames = "year"
    sortReversed = True

