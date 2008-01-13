import ceDatabase
import ceGUI

class EditWindow(ceGUI.GridEditWindow):
    title = "Elders"

    def OnCreate(self):
        self.AddSubWindow(DistrictSubWindow)


class Grid(ceGUI.Grid):
    
    def OnCreate(self):
        self.AddColumn(ceGUI.GridColumnStr, "Name", "name")


class DataSet(ceDatabase.DataSet):
    tableName = "Elders"
    attrNames = "elderId name"
    pkAttrNames = "elderId"
    pkIsGenerated = True
    pkSequenceName = "ElderId_s"


class DistrictSubWindow(ceGUI.SubWindow):
    childWindowName = "w_ElderDistricts.EditWindow"
    label = "District"

