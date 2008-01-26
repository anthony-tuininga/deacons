import ceDatabase
import ceGUI
import cx_Exceptions
import wx

import Common

class Panel(ceGUI.Panel):

    def OnCreate(self):
        self.depositedDateLabel = self.AddLabel()
        self.notebook = ceGUI.Notebook(self)
        for cls in (CollectionsPanel, ChequesPanel):
            page = cls(self.notebook)
            page.RestoreSettings()
            self.notebook.AddPage(page, page.labelText)

    def OnLayout(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.depositedDateLabel, flag = wx.ALL, border = 5)
        sizer.Add(self.notebook, flag = wx.EXPAND, proportion = 1)
        return sizer

    def Retrieve(self, depositId, dateDeposited):
        label = "Deposited %s" % dateDeposited.strftime("%A, %B %d, %Y")
        self.depositedDateLabel.SetLabel(label)
        for page in self.notebook.IterPages():
            page.list.Retrieve(depositId)

    def RestoreSettings(self):
        for page in self.notebook.IterPages():
            page.RestoreSettings()

    def SaveSettings(self):
        for page in self.notebook.IterPages():
            page.SaveSettings()


class SubPanel(ceGUI.DataListPanel):

    def RestoreSettings(self):
        self.list.RestoreColumnWidths(self.settingsName)

    def SaveSettings(self):
        self.list.SaveColumnWidths(self.settingsName)


class CollectionsPanel(SubPanel):
    listClassName = "CollectionsList"
    settingsName = "CollectionsColumnWidths"
    labelText = "Collections"


class CollectionsList(ceGUI.DataList):
    dataSetClassName = "CollectionsDataSet"

    def OnCreate(self):
        self.AddColumn("dateCollected", "Date", 150, cls = DateColumn)
        self.AddColumn("causeId", "Cause", 225, cls = Common.CauseColumn)
        self.AddColumn("description", "Description")


class CollectionsDataSet(ceDatabase.DataSet):
    tableName = "Collections"
    attrNames = "collectionId causeId dateCollected reconciled description"
    retrievalAttrNames = "depositId"
    pkAttrNames = "collectionId"


class ChequesPanel(SubPanel):
    listClassName = "ChequesList"
    settingsName = "ChequesColumnWidths"
    labelText = "Cheques"


class ChequesList(ceGUI.DataList):
    dataSetClassName = "ChequesDataSet"

    def OnCreate(self):
        self.AddColumn("chequeNumber", "Number", 75)
        self.AddColumn("causeId", "Cause", 225, cls = Common.CauseColumn)
        self.AddColumn("amount", "Amount", cls = Common.AmountColumn,
                justification = wx.LIST_FORMAT_RIGHT)


class ChequesDataSet(ceDatabase.DataSet):
    attrNames = "chequeId chequeNumber causeId amount"
    retrievalAttrNames = "depositId"
    pkAttrNames = "chequeId"

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
                where ChequeId in
                    ( select ca.ChequeId
                      from
                        Collections c
                        join ChequeAmounts ca
                            on ca.CollectionId = c.CollectionId
                      where c.DepositId = ?
                    )
                order by ChequeNumber"""


class DateColumn(ceGUI.ListDateColumn):
    dateFormat = "%b/%d/%Y (%a)"

