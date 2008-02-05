import ceDatabase
import ceGUI

class Panel(ceGUI.DataListPanel):
    editDialogName = "w_CauseEdit.Dialog"


class List(ceGUI.DataList):

    def OnCreate(self):
        self.AddColumn("description", "Description")


class DataSet(ceDatabase.DataSet):
    tableName = "Causes"
    attrNames = "causeId description"
    pkAttrNames = "causeId"

