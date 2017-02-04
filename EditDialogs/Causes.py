"""
Dialog for editing causes.
"""

import ceGUI

import Models

class Dialog(ceGUI.EditDialog):
    title = "Edit Cause"
    defaultWidth = 280

    def OnNewRow(self, parent, row):
        row.isActive = row.isReported = True


class Panel(ceGUI.DataEditPanel):

    def OnCreate(self):
        ceGUI.TextEditDialogColumn(self, "description", "Description:",
                maxLength = 60, required = True)
        ceGUI.TextEditDialogColumn(self, "address", "Address:",
                multiLine= True, size = (-1, 105))
        ceGUI.BooleanEditDialogColumn(self, "isReported", "Reported?")
        ceGUI.BooleanEditDialogColumn(self, "isActive", "Active?")


class DataSet(ceGUI.DataSet):
    rowClass = Models.Causes
    retrievalAttrNames = "causeId"
    pkSequenceName = "CauseId_s"
    pkIsGenerated = True

