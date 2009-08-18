"""
Edit dialog for elders.
"""

import ceDatabase
import ceGUI

class Panel(ceGUI.DataListPanel):
    editDialogName = "EditDialogs.Elders.Dialog"


class List(ceGUI.DataList):

    def OnCreate(self):
        self.AddColumn("name", "Name")


class DataSet(ceDatabase.DataSet):
    tableName = "Elders"
    attrNames = "elderId name"
    pkAttrNames = "elderId"

