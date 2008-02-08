"""
Dialog for editing cash.
"""

import ceDatabase
import ceGUI
import decimal
import wx

class Dialog(ceGUI.StandardDialog):
    title = "Edit Cash"

    def OnCreate(self):
        parent = self.GetParent()
        self.notebook = ceGUI.Notebook(self)
        self.collection = parent.list.contextItem
        cursor = self.config.connection.cursor()
        cursor.execute("""
                select CauseId
                from CollectionCauses
                where CollectionId = ?""",
                self.collection.collectionId)
        causes = [self.config.cache.CauseForId(i) for i, in cursor]
        itemsToSort = [(c.description.upper(), c) for c in causes]
        causes = [c for k, c in sorted(itemsToSort)]
        for cause in causes:
            page = Panel(self.notebook)
            self.notebook.AddPage(page, cause.description)

    def OnLayout(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.notebook, flag = wx.EXPAND | wx.ALL, proportion = 1,
                border = 5)
        return sizer


class Panel(ceGUI.Panel):

    def CreateSizer(self, fields):
        sizer = wx.FlexGridSizer(rows = len(fields), cols = 4, vgap = 5,
                hgap = 5)
        for field in fields:
            field.AddToSizer(sizer)
        return sizer

    def OnCreate(self):
        self.coinFields = []
        self.cashFields = []
        Field(self, 1, "0.01", "roll(s) of pennies", 50)
        Field(self, 2, "0.05", "roll(s) of nickels", 40)
        Field(self, 3, "0.10", "roll(s) of dimes", 50)
        Field(self, 4, "0.25", "roll(s) of quarters", 40)
        Field(self, 5, "1.00", "roll(s) of $1 coins", 25)
        Field(self, 5, "2.00", "roll(s) of $2 coins", 25)
        Field(self, 7, "5.00", "$5 bill(s)", 1)
        Field(self, 8, "10.00", "$10 bill(s)", 1)
        Field(self, 9, "20.00", "$20 bill(s)", 1)
        Field(self, 10, "50.00", "$50 bill(s)", 1)
        Field(self, 11, "100.00", "$100 bill(s)", 1)

    def OnLayout(self):
        coinFieldsSizer = self.CreateSizer(self.coinFields)
        cashFieldsSizer = self.CreateSizer(self.cashFields)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(coinFieldsSizer, flag = wx.ALL | wx.EXPAND, border = 5)
        sizer.Add(cashFieldsSizer, flag = wx.ALL | wx.EXPAND, border = 5)
        return sizer


class Field(object):

    def __init__(self, parent, cashDenominationId, stringValue, label,
            quantityMultiple):
        self.cashDenominationId = cashDenominationId
        self.value = decimal.Decimal(stringValue)
        self.quantityMultiple = quantityMultiple
        self.quantityField = wx.SpinCtrl(parent, min = 0, max = 9999,
                value = "0")
        self.label = parent.AddLabel(label)
        self.equalsLabel = parent.AddLabel("=")
        self.totalValueField = parent.AddTextField(wx.TE_READONLY)
        if quantityMultiple == 1:
            parent.cashFields.append(self)
        else:
            parent.coinFields.append(self)

    def AddToSizer(self, sizer):
        sizer.Add(self.quantityField, flag = wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.label, flag = wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.equalsLabel, flag = wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.totalValueField, flag = wx.ALIGN_CENTER_VERTICAL)

