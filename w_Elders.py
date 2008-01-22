import ceDatabase
import ceGUI

class Panel(ceGUI.DataListPanel):
    pass


class List(ceGUI.DataList):

    def OnCreate(self):
        self.AddColumn("name", "Name")


class DataSet(ceDatabase.DataSet):
    tableName = "Elders"
    attrNames = "elderId name"
    pkAttrNames = "elderId"

