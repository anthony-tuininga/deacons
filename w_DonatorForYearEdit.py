"""
Dialog for editing assigned number for donators for a given year.
"""

import ceDatabase
import ceGUI
import wx

class Dialog(ceGUI.EditDialog):
    title = "Edit Donator Number"

    def OnCreate(self):
        self.AddColumn("name", "Name:", self.AddTextField(wx.TE_READONLY))
        self.AddColumn("assignedNumber", "Number:", self.AddIntegerField(),
                required = True)

    def OnNewRow(self, parent, row):
        year, = parent.list.dataSet.retrievalArgs
        row.year = year
        dialog = parent.OpenWindow("w_SelectDonator.Dialog")
        existingValues = dict.fromkeys(d.donatorId \
                for d in parent.list.dataSet.rows.itervalues())
        donators = [d for d in parent.config.cache.Donators() \
                if d.active and d.donatorId not in existingValues]
        dialog.Retrieve(donators)
        if dialog.ShowModal() == wx.ID_OK:
            donator = dialog.GetSelectedItem()
            row.donatorId = donator.donatorId
        dialog.Destroy()

    def Retrieve(self, parent):
        super(Dialog, self).Retrieve(parent)
        row = self.dataSet.rows[0]
        if row.donatorId is None:
            row.name = None
        else:
            donator = parent.config.cache.DonatorForId(row.donatorId)
            row.name = donator.name


class DataSet(ceDatabase.DataSet):
    tableName = "DonatorsForYear"
    attrNames = "year donatorId assignedNumber"
    extraAttrNames = "name"
    retrievalAttrNames = pkAttrNames = "year donatorId"

