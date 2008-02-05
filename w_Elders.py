import ceDatabase
import ceGUI

class Panel(ceGUI.DataListPanel):
    editDialogName = "w_ElderEdit.Dialog"


class List(ceGUI.DataList):

    def OnCreate(self):
        self.AddColumn("name", "Name")


class DataSet(ceDatabase.DataSet):
    tableName = "Elders"
    attrNames = "elderId name"
    pkAttrNames = "elderId"

