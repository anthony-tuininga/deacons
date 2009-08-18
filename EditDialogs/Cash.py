"""
Dialog for editing cash.
"""

import ceDatabase
import ceGUI
import decimal
import wx

import Common

class Dialog(ceGUI.StandardDialog):

    def GetKeyedDataSet(self):
        return ceDatabase.KeyedDataSet(self.dataSet, "causeId",
                "cashDenominationId")

    def OnCreate(self):
        parent = self.GetParent()
        self.notebook = ceGUI.Notebook(self)
        self.collection = parent.list.GetSelectedItem()
        title = "Edit Cash - %s" % \
                self.collection.dateCollected.strftime("%A, %B %d, %Y")
        self.SetTitle(title)
        cursor = self.config.connection.cursor()
        self.dataSet = DataSet(self.config.connection)
        self.dataSet.Retrieve(self.collection.collectionId)
        keyedDataSet = self.GetKeyedDataSet()
        cursor.execute("""
                select CauseId
                from CollectionCauses
                where CollectionId = ?""",
                self.collection.collectionId)
        causeIds = [i for i, in cursor]
        for cause in self.config.cache.Causes():
            if cause.causeId not in causeIds:
                continue
            page = Panel(self.notebook)
            page.Populate(keyedDataSet, cause)
            self.notebook.AddPage(page, cause.description)

    def OnLayout(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.notebook, flag = wx.EXPAND | wx.ALL, border = 5)
        return sizer

    def OnOk(self):
        keyedDataSet = self.GetKeyedDataSet()
        for page in self.notebook.IterPages():
            page.Update(self.collection, keyedDataSet)
        self.dataSet.Update()

    def RestoreSettings(self):
        pass

    def SaveSettings(self):
        pass


class Panel(ceGUI.Panel):

    def CreateSizer(self, fields, staticBox):
        fieldsSizer = wx.FlexGridSizer(rows = len(fields), cols = 4, vgap = 5,
                hgap = 5)
        for field in fields:
            field.AddToSizer(fieldsSizer)
        sizer = wx.StaticBoxSizer(staticBox, wx.VERTICAL)
        sizer.Add(fieldsSizer, flag = wx.ALL | wx.EXPAND, border = 5)
        return sizer

    def OnCreate(self):
        self.fields = []
        self.fieldsById = {}
        self.coinsStaticBox = wx.StaticBox(self, label = "Coin")
        self.cashStaticBox = wx.StaticBox(self, label = "Coin")
        Field(self, 1, "0.01", "roll(s) of pennies", 50)
        Field(self, 2, "0.05", "roll(s) of nickels", 40)
        Field(self, 3, "0.10", "roll(s) of dimes", 50)
        Field(self, 4, "0.25", "roll(s) of quarters", 40)
        Field(self, 5, "1.00", "roll(s) of $1 coins", 25)
        Field(self, 6, "2.00", "roll(s) of $2 coins", 25)
        Field(self, 7, "5.00", "$5 bill(s)", 1)
        Field(self, 8, "10.00", "$10 bill(s)", 1)
        Field(self, 9, "20.00", "$20 bill(s)", 1)
        Field(self, 10, "50.00", "$50 bill(s)", 1)
        Field(self, 11, "100.00", "$100 bill(s)", 1)
        afterThis = self.fields[-1].quantityField
        for field in self.fields:
            field.totalValueField.MoveAfterInTabOrder(afterThis)
            afterThis = field.totalValueField

    def OnLayout(self):
        coinFields = [f for f in self.fields if f.quantityMultiple > 1]
        cashFields = [f for f in self.fields if f.quantityMultiple == 1]
        coinFieldsSizer = self.CreateSizer(coinFields, self.coinsStaticBox)
        cashFieldsSizer = self.CreateSizer(cashFields, self.cashStaticBox)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(coinFieldsSizer, flag = wx.ALL | wx.EXPAND, border = 5)
        sizer.Add(cashFieldsSizer, flag = wx.ALL | wx.EXPAND, border = 5)
        return sizer

    def Populate(self, keyedDataSet, cause):
        self.cause = cause
        for field in self.fields:
            row = keyedDataSet.FindRow(cause.causeId,
                    field.cashDenominationId)
            if row is None:
                value = 0
            else:
                value = row.quantity / field.quantityMultiple
            field.quantityField.SetValue(value)
            field.SetTotalValue(value)

    def Update(self, collection, keyedDataSet):
        for field in self.fields:
            quantity = field.GetQuantity()
            if quantity == 0:
                keyedDataSet.DeleteRow(self.cause.causeId,
                        field.cashDenominationId)
            else:
                row = keyedDataSet.FindRow(self.cause.causeId,
                        field.cashDenominationId)
                if row is None:
                    row = keyedDataSet.InsertRow()
                    row.collectionId = collection.collectionId
                    row.causeId = self.cause.causeId
                    row.cashDenominationId = field.cashDenominationId
                row.quantity = quantity


class Field(object):

    def __init__(self, parent, cashDenominationId, stringValue, label,
            quantityMultiple):
        self.cashDenominationId = cashDenominationId
        self.value = decimal.Decimal(stringValue)
        self.quantityMultiple = quantityMultiple
        self.quantityField = wx.SpinCtrl(parent, min = 0, max = 9999)
        parent.BindEvent(self.quantityField, wx.EVT_SPINCTRL,
                method = self.OnQuantitySet)
        self.label = parent.AddLabel(label)
        self.equalsLabel = parent.AddLabel("=")
        self.totalValueField = parent.AddTextField(wx.TE_READONLY)
        parent.fields.append(self)
        parent.fieldsById[cashDenominationId] = self

    def AddToSizer(self, sizer):
        sizer.Add(self.quantityField, flag = wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.label, flag = wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.equalsLabel, flag = wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.totalValueField, flag = wx.ALIGN_CENTER_VERTICAL)

    def GetQuantity(self):
        return self.quantityField.GetValue() * self.quantityMultiple

    def OnQuantitySet(self, event):
        self.SetTotalValue(self.quantityField.GetValue())

    def SetTotalValue(self, value):
        totalValue = value * self.quantityMultiple * self.value
        self.totalValueField.SetValue(Common.FormattedAmount(totalValue))


class DataSet(ceDatabase.DataSet):
    tableName = "CollectionCash"
    attrNames = """collectionCashId collectionId causeId cashDenominationId
            quantity"""
    pkAttrNames = "collectionCashId"
    retrievalAttrNames = "collectionId"
    pkSequenceName = "CollectionCashId_s"
    pkIsGenerated = True

