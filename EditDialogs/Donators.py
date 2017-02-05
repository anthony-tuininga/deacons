"""
Dialog for editing donators.
"""

import ceGUI

import Models

class Dialog(ceGUI.EditDialog):
    title = "Edit Donator"
    defaultWidth = 280

    def OnNewRow(self, parent, row):
        row.isActive = True


class Panel(ceGUI.DataEditPanel):

    def OnCreate(self):
        ceGUI.TextEditDialogColumn(self, "lastName", "Last Name:",
                maxLength = 30, required = True)
        ceGUI.TextEditDialogColumn(self, "givenNames", "Given Names:",
                maxLength = 50)
        ceGUI.TextEditDialogColumn(self, "address", "Address:",
                multiLine= True, size = (-1, 105))
        ceGUI.BooleanEditDialogColumn(self, "isActive", "Active?")


class DataSet(ceGUI.DataSet):
    rowClass = Models.Donators
    retrievalAttrNames = "donatorId"
    pkSequenceName = "DonatorId_s"
    pkIsGenerated = True

