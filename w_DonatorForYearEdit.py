"""
Dialog for editing assigned number for donators for a given year.
"""

import ceDatabase
import ceGUI
import wx

class Dialog(ceGUI.EditDialog):
    title = "Edit Donator Number"

    def OnNewRow(self, parent, row):
        cache, row.year = parent.list.dataSet.retrievalArgs
        dialog = parent.OpenWindow("w_SelectDonator.Dialog")
        existingValues = dict.fromkeys(d.donatorId \
                for d in parent.list.dataSet.rows.itervalues())
        donators = [d for d in parent.config.cache.Donators() \
                if d.isActive and d.donatorId not in existingValues]
        dialog.Retrieve(donators)
        if dialog.ShowModal() == wx.ID_OK:
            donator = dialog.GetSelectedItem()
            row.donatorId = donator.donatorId
        dialog.Destroy()


class Panel(ceGUI.DataEditPanel):

    def OnCreate(self):
        self.AddColumn("name", "Name:", self.AddTextField(wx.TE_READONLY))
        self.AddColumn("assignedNumber", "Number:", self.AddIntegerField(),
                required = True)

    def OnPostCreate(self):
        row = self.GetRow()
        if row.donatorId is None:
            row.name = None
        else:
            donator = self.config.cache.DonatorForId(row.donatorId)
            row.name = donator.name
        super(Panel, self).OnPostCreate()

    def OnPostUpdate(self):
        self.cache.donatorsForYear.Clear()


class DataSet(ceDatabase.DataSet):
    tableName = "DonatorsForYear"
    attrNames = "year donatorId assignedNumber"
    extraAttrNames = "name"
    retrievalAttrNames = pkAttrNames = "year donatorId"

