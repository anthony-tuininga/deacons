"""
Dialog for editing whether a cause is deductible for a given year.
"""

import ceDatabase
import ceGUI
import wx

class Dialog(ceGUI.EditDialog):
    title = "Edit Cause Deductiblity"

    def OnCreate(self):
        self.AddColumn("description", "Description:",
                self.AddTextField(wx.TE_READONLY))
        self.AddColumn("deductible", "Deductible:", self.AddCheckBox())

    def OnNewRow(self, parent, row):
        year, = parent.list.dataSet.retrievalArgs
        row.year = year
        dialog = parent.OpenWindow("w_SelectCause.Dialog")
        existingValues = dict.fromkeys(d.causeId \
                for d in parent.list.dataSet.rows.itervalues())
        causes = [d for d in parent.config.cache.Causes() \
                if d.active and d.causeId not in existingValues]
        dialog.Retrieve(causes)
        if dialog.ShowModal() == wx.ID_OK:
            cause = dialog.GetSelectedItem()
            row.causeId = cause.causeId
        dialog.Destroy()

    def Retrieve(self, parent):
        super(Dialog, self).Retrieve(parent)
        row = self.dataSet.rows[0]
        if row.causeId is None:
            row.description = None
        else:
            cause = parent.config.cache.CauseForId(row.causeId)
            row.description = cause.description


class DataSet(ceDatabase.DataSet):
    tableName = "CausesForYear"
    attrNames = "year causeId deductible"
    extraAttrNames = "description"
    retrievalAttrNames = pkAttrNames = "year causeId"
    charBooleanAttrNames = "deductible"

