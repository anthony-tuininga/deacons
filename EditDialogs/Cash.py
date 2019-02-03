"""
Dialog for editing cash.
"""

import ceGUI
import wx

import Models

class Dialog(ceGUI.EditDialog):

    def OnOk(self):
        transaction = self.config.dataSource.BeginTransaction()
        row = self.GetRow()
        for field in self.panel.coinsFields + self.panel.billsFields:
            cashDenom = field.cashDenomination
            newQuantity = field.GetQuantity()
            origCashRow = row.cashDict.get(cashDenom.cashDenominationId)
            if origCashRow is None and newQuantity > 0:
                setValues = dict(trayId = row.trayId,
                        cashDenominationId = cashDenom.cashDenominationId,
                        quantity = newQuantity)
                transaction.AddItem(tableName = "Cash",
                        pkSequenceName = "CashId_s", pkAttrName = "CashId",
                        setValues = setValues)
            elif origCashRow is not None and newQuantity == 0:
                transaction.AddItem(tableName = "Cash",
                        conditions = dict(cashId = origCashRow.cashId))
            elif origCashRow is not None and \
                    newQuantity != origCashRow.quantity:
                transaction.AddItem(tableName = "Cash",
                        setValues = dict(quantity = newQuantity),
                        conditions = dict(cashId = origCashRow.cashId))
        self.config.dataSource.CommitTransaction(transaction)

    def OnPostCreate(self):
        row = self.GetRow()
        self.panel.Populate(row.cashDict)

    def Retrieve(self, parent):
        row = self.dataSet.rowClass.New()
        row.trayId = self.parentItem.trayId
        row.cashDict = {}
        for cashRow in Models.Cash.GetRows(parent.config.dataSource,
                trayId = row.trayId):
            row.cashDict[cashRow.cashDenominationId] = cashRow
        self.dataSet.SetRows([row])


class Panel(ceGUI.DataPanel):

    def __CreateSizer(self, fields, staticBox):
        fieldsSizer = wx.FlexGridSizer(rows = len(fields), cols = 4, vgap = 5,
                hgap = 5)
        for field in fields:
            field.AddToSizer(fieldsSizer)
        sizer = wx.StaticBoxSizer(staticBox, wx.VERTICAL)
        sizer.Add(fieldsSizer, flag = wx.ALL | wx.EXPAND, border = 5)
        return sizer

    def OnCreate(self):
        self.coinsFields = []
        self.billsFields = []
        self.coinsStaticBox = wx.StaticBox(self, label = "Coin")
        self.billsStaticBox = wx.StaticBox(self, label = "Bills")
        for row in Models.CashDenominations.GetRows(self.config.dataSource):
            field = Field(self, row)
            if row.quantityMultiple == 1:
                self.billsFields.append(field)
            else:
                self.coinsFields.append(field)

    def OnLayout(self):
        coinsFieldsSizer = self.__CreateSizer(self.coinsFields,
                self.coinsStaticBox)
        billsFieldsSizer = self.__CreateSizer(self.billsFields,
                self.billsStaticBox)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(coinsFieldsSizer, flag = wx.ALL | wx.EXPAND, border = 5,
                proportion = 1)
        sizer.Add(billsFieldsSizer, flag = wx.ALL | wx.EXPAND, border = 5,
                proportion = 1)
        return sizer

    def Populate(self, cashDict):
        for field in self.coinsFields + self.billsFields:
            cashRow = cashDict.get(field.cashDenomination.cashDenominationId)
            if cashRow is None:
                field.SetQuantity(0)
            else:
                field.SetQuantity(cashRow.quantity)


class DataSet(ceGUI.DataSet):
    attrNames = "trayId cashDict"


class Field(object):

    def __init__(self, parent, cashDenomination):
        self.cashDenomination = cashDenomination
        self.quantityField = wx.SpinCtrl(parent, min = 0, max = 9999)
        parent.BindEvent(self.quantityField, wx.EVT_SPINCTRL,
                method = self.OnQuantitySet)
        self.label = parent.AddLabel(cashDenomination.description)
        self.equalsLabel = parent.AddLabel("=")
        self.totalValueField = parent.AddTextField(wx.TE_READONLY)

    def AddToSizer(self, sizer):
        sizer.Add(self.quantityField, flag = wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.label, flag = wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.equalsLabel, flag = wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.totalValueField, flag = wx.ALIGN_CENTER_VERTICAL,
                proportion = 1)

    def GetQuantity(self):
        return self.quantityField.GetValue() * \
                self.cashDenomination.quantityMultiple

    def OnQuantitySet(self, event):
        self.SetTotalValue(self.quantityField.GetValue())

    def SetQuantity(self, value):
        quantity = value / self.cashDenomination.quantityMultiple
        self.quantityField.SetValue(quantity)
        self.SetTotalValue(quantity)

    def SetTotalValue(self, value):
        totalValue = value * self.cashDenomination.quantityMultiple * \
                self.cashDenomination.value
        displayValue = "${0:,.2f}".format(totalValue)
        self.totalValueField.SetValue(displayValue)

