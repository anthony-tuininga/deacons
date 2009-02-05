"""
Dialog for editing collections.
"""

import ceDatabase
import ceGUI
import datetime
import wx

class Dialog(ceGUI.EditDialog):
    title = "Edit Cause"

    def OnNewRow(self, parent, row):
        depositsPanel = parent.GetParent().GetParent()
        row.reconciled = False
        row.depositId = depositsPanel.depositId
        row.dateCollected = datetime.date.today()
        causes = parent.config.cache.Causes()
        if causes:
            row.causeId = causes[0].causeId


class Panel(ceGUI.DataEditPanel):

    def OnCreate(self):
        self.AddColumn("dateCollected", "Date:", self.AddDateField(),
                required = True)
        choices = [(c.causeId, c.description) \
                for c in self.config.cache.Causes()]
        self.causeField = self.AddChoiceField(*choices)
        self.AddColumn("causeId", "Cause:", self.causeField, required = True)
        self.AddColumn("description", "Description:",
                self.AddTextField(maxLength = 60))
        self.AddColumn("reconciled", "Reconciled?", self.AddCheckBox())


class DataSet(ceDatabase.DataSet):
    tableName = "Collections"
    attrNames = """collectionId dateCollected causeId reconciled depositId
            description"""
    charBooleanAttrNames = "reconciled"
    retrievalAttrNames = pkAttrNames = "collectionId"
    pkSequenceName = "CollectionId_s"
    pkIsGenerated = True

    def InsertRowInDatabase(self, cursor, row):
        super(DataSet, self).InsertRowInDatabase(cursor, row)
        cursor.execute("""
                insert into CollectionCauses
                (CollectionId, CauseId)
                values (?, ?)""",
                row.collectionId, row.causeId)
        app = wx.GetApp()
        cause = app.config.cache.CauseForId(row.causeId)
        if cause.address is not None:
            cursor.execute("""
                    insert into UnremittedAmounts
                    (CollectionId, CauseId)
                    values (?, ?)""",
                    row.collectionId, row.causeId)
        if row.dateCollected.weekday() == 6: # Sunday
            cursor.execute("""
                    insert into CollectionCauses
                    (CollectionId, CauseId)
                    values (?, 1)""",
                    row.collectionId)

