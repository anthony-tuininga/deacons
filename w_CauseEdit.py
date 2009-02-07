"""
Dialog for editing causes.
"""

import ceDatabase
import ceGUI
import wx

class Dialog(ceGUI.EditDialog):
    title = "Edit Cause"

    def OnNewRow(self, parent, row):
        row.isActive = row.isReported = True


class Panel(ceGUI.DataEditPanel):
    updateSubCacheAttrName = "causes"

    def OnCreate(self):
        self.AddColumn("description", "Description:",
                self.AddTextField(maxLength = 60), required = True)
        field = self.AddTextField(maxLength = 250, style = wx.TE_MULTILINE,
                size = (-1, 105))
        self.AddColumn("address", "Address:", field)
        self.AddColumn("isReported", "Reported?", self.AddCheckBox())
        self.AddColumn("isActive", "Active?", self.AddCheckBox())


class DataSet(ceDatabase.DataSet):
    tableName = "Causes"
    attrNames = "causeId description address isReported isActive"
    charBooleanAttrNames = "isReported isActive"
    retrievalAttrNames = pkAttrNames = "causeId"
    pkSequenceName = "CauseId_s"
    pkIsGenerated = True

