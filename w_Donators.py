import ceDatabase
import ceGUI

class Panel(ceGUI.DataListPanel):
    editDialogName = "w_DonatorEdit.Dialog"


class List(ceGUI.DataList):

    def OnCreate(self):
        self.AddColumn("lastName", "Last Name", 200)
        self.AddColumn("givenNames", "Given Names")


class DataSet(ceDatabase.DataSet):
    tableName = "Donators"
    attrNames = "donatorId givenNames lastName"
    pkAttrNames = "donatorId"

