"""
Dialog for editing elders.
"""

import ceDatabase
import ceGUI

class Dialog(ceGUI.EditDialog):
    title = "Edit Elder"
    defaultWidth = 280


class Panel(ceGUI.DataEditPanel):

    def OnCreate(self):
        self.AddColumn("name", "Name:", self.AddTextField(maxLength = 60),
                required = True)


class DataSet(ceDatabase.DataSet):
    tableName = "Elders"
    attrNames = "elderId name"
    retrievalAttrNames = pkAttrNames = "elderId"
    pkIsGenerated = True
    pkSequenceName = "ElderId_s"

