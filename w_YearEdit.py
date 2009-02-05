"""
Dialog for editing years.
"""

import ceDatabase
import ceGUI
import wx

import Common

class Dialog(ceGUI.EditDialog):
    title = "Edit Year"


class Panel(ceGUI.DataEditPanel):

    def OnCreate(self):
        parent = self.GetParent()
        if parent.parentItem is not None:
            style = wx.TE_READONLY
        else:
            style = 0
        self.AddColumn("year", "Year:",
                self.AddIntegerField(style = style), required = True)
        self.AddColumn("budgetAmount", "Budget:", Common.AmountField(self),
                required = True)
        self.AddColumn("promptForReceiptGeneration", "Receipts Prompt?",
                self.AddCheckBox())
        self.AddColumn("receiptsIssued", "Receipts Issued?",
                self.AddCheckBox())


class DataSet(ceDatabase.DataSet):
    tableName = "Years"
    attrNames = "year budgetAmount promptForReceiptGeneration receiptsIssued"
    charBooleanAttrNames = "promptForReceiptGeneration receiptsIssued"
    retrievalAttrNames = pkAttrNames = "year"

