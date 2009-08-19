"""
Dialog for editing cheques.
"""

import ceDatabase
import ceGUI
import wx

import Common

class Dialog(ceGUI.EditDialog):
    title = "Edit Cheque"
    defaultWidth = 350

    def OnNewRow(self, parent, row):
        depositId = parent.GetParent().GetParent().depositId
        dialog = parent.OpenWindow("SelectDialogs.Unremitted.Dialog")
        dialog.Retrieve(depositId)
        if dialog.ShowModal() == wx.ID_OK:
            selectedItem = dialog.GetSelectedItem()
            row.causeId = selectedItem.causeId
            row.amount = selectedItem.amount
        dialog.Destroy()


class Panel(ceGUI.DataEditPanel):

    def OnCreate(self):
        self.AddColumn("chequeNumber", "Cheque Number:",
                self.AddTextField(cls = ceGUI.IntegerField),
                required = True)
        self.AddColumn("causeId", "Cause:",
                self.AddTextField(style = wx.TE_READONLY), cls = CauseColumn)
        self.AddColumn("amount", "Amount:",
                self.AddTextField(style = wx.TE_READONLY), cls = AmountColumn)


class DataSet(ceDatabase.DataSet):
    tableName = "Cheques"
    attrNames = "chequeId chequeNumber causeId amount"
    retrievalAttrNames = pkAttrNames = "chequeId"
    insertAttrNames = "chequeId chequeNumber causeId"
    updateAttrNames = "chequeNumber"
    pkSequenceName = "ChequeId_s"
    pkIsGenerated = True

    def _GetSqlForRetrieve(self):
        return """
                select
                  ChequeId,
                  ChequeNumber,
                  CauseId,
                  ( select sum(ca.ChequeAmount + ca.CashAmount)
                    from
                      ChequeAmounts cqa
                      join CollectionAmounts ca
                          on ca.CollectionId = cqa.CollectionId
                          and ca.CauseId = cqa.CauseId
                    where cqa.ChequeId = c.ChequeId
                  )
                from Cheques c
                where ChequeId = ?"""

    def InsertRowInDatabase(self, cursor, row):
        super(DataSet, self).InsertRowInDatabase(cursor, row)
        cursor.execute("""
                insert into ChequeAmounts
                (ChequeId, CollectionId, CauseId)
                select ?, CollectionId, CauseId
                from UnremittedAmounts
                where CauseId = ?""",
                row.chequeId, row.causeId)
        cursor.execute("""
                delete from UnremittedAmounts
                where CauseId = ?""",
                row.causeId)


class CauseColumn(ceGUI.EditDialogColumn):

    def SetValue(self, row):
        if row.causeId is not None:
            cause = self.config.cache.CauseForId(row.causeId)
            self.field.SetValue(cause.description)


class AmountColumn(ceGUI.EditDialogColumn):

    def SetValue(self, row):
        if row.amount is not None:
            self.field.SetValue(Common.FormattedAmount(row.amount))

