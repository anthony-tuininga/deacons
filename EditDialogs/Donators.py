"""
Dialog for editing donators.
"""

import ceDatabase
import ceGUI
import wx

class Dialog(ceGUI.EditDialog):
    title = "Edit Donator"
    defaultWidth = 280

    def OnNewRow(self, parent, row):
        row.isActive = True


class Panel(ceGUI.DataEditPanel):
    updateSubCacheAttrName = "donators"

    def OnCreate(self):
        self.AddColumn("lastName", "Last Name:",
                self.AddTextField(maxLength = 30), required = True)
        self.AddColumn("givenNames", "Given Names:",
                self.AddTextField(maxLength = 50))
        field = self.AddTextField(maxLength = 150, style = wx.TE_MULTILINE,
                size = (-1, 105))
        self.AddColumn("address", "Address:", field)
        self.AddColumn("isActive", "Active?", self.AddCheckBox())


class DataSet(ceDatabase.DataSet):
    tableName = "Donators"
    attrNames = "donatorId givenNames lastName address isActive"
    charBooleanAttrNames = "isActive"
    retrievalAttrNames = pkAttrNames = "donatorId"
    pkSequenceName = "DonatorId_s"
    pkIsGenerated = True

