import ceDatabase
import ceGUI
import cx_Exceptions
import wx

import Common

class Panel(Common.Panel):

    def OnBankChequesReport(self, event):
        self.PrintReport("ReportDefs.DepositedCheques", self.depositId,
                self.dateDeposited)

    def OnBankReport(self, event):
        self.PrintReport("ReportDefs.DepositSummary", self.depositId,
                self.dateDeposited)

    def OnChequesReport(self, event):
        self.PrintReport("ReportDefs.DepositCheques", self.depositId,
                self.dateDeposited)

    def OnCreate(self):
        self.notebook = ceGUI.Notebook(self)
        for cls in (CollectionsPanel, ChequesPanel):
            page = cls(self.notebook)
            page.RestoreSettings()
            self.notebook.AddPage(page, page.labelText)
        self.staticBox = wx.StaticBox(self, -1, "Reports")
        self.bankReportButton = self.AddButton("Bank",
                method = self.OnBankReport)
        self.bankChequesReportButton = self.AddButton("Bank Cheques",
                method = self.OnBankChequesReport)
        self.treasurerReportButton = self.AddButton("Treasurer",
                method = self.OnTreasurerReport)
        self.chequesReportButton = self.AddButton("Cheques",
                method = self.OnChequesReport)

    def OnLayout(self):
        buttonSizer = wx.StaticBoxSizer(self.staticBox, wx.HORIZONTAL)
        buttonSizer.Add(self.bankReportButton, flag = wx.ALL, border = 5)
        buttonSizer.Add(self.bankChequesReportButton, flag = wx.ALL,
                border = 5)
        buttonSizer.Add(self.treasurerReportButton, flag = wx.ALL, border = 5)
        buttonSizer.Add(self.chequesReportButton, flag = wx.ALL, border = 5)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(buttonSizer, flag = wx.ALL, border = 5)
        sizer.Add(self.notebook, flag = wx.EXPAND | wx.ALL, proportion = 1,
                border = 5)
        return sizer

    def OnTreasurerReport(self, event):
        self.PrintReport("ReportDefs.TreasurerSummary", self.depositId)

    def Retrieve(self, depositId, dateDeposited):
        self.depositId = depositId
        self.dateDeposited = dateDeposited
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
    editDialogName = "EditDialogs.Collections.Dialog"
    settingsName = "CollectionsColumnWidths"
    labelText = "Collections"


class CollectionsList(ceGUI.DataList):
    dataSetClassName = "CollectionsDataSet"

    def _CreateContextMenu(self):
        super(CollectionsList, self)._CreateContextMenu()
        self.menu.AddSeparator()
        self.editCashMenuItem = self.menu.AddEntry(self, "Edit Cash...",
                method = self.OnEditCash, passEvent = False)
        self.editDonationsMenuItem = self.menu.AddEntry(self,
                "Edit Donations...", method = self.OnEditDonations,
                passEvent = False)

    def OnContextMenu(self):
        enabled = (len(self.GetSelectedItems()) == 1)
        self.editCashMenuItem.Enable(enabled)
        self.editDonationsMenuItem.Enable(enabled)
        super(CollectionsList, self).OnContextMenu()

    def OnCreate(self):
        self.AddColumn("dateCollected", "Date", 150, cls = DateColumn)
        self.AddColumn("causeId", "Cause", 225, cls = Common.CauseColumn)
        self.AddColumn("chequeAmount", "Cheques", 150,
                cls = Common.AmountColumn,
                justification = wx.LIST_FORMAT_RIGHT)
        self.AddColumn("cashAmount", "Cash", 150, cls = Common.AmountColumn,
                justification = wx.LIST_FORMAT_RIGHT)
        self.AddColumn("description", "Description")

    def OnEditCash(self):
        parent = self.GetParent()
        dialog = parent.OpenWindow("EditDialogs.Cash.Dialog")
        dialog.ShowModal()
        dialog.Destroy()

    def OnEditDonations(self):
        parent = self.GetParent()
        dialog = parent.OpenWindow("EditDialogs.Donations.Dialog")
        dialog.ShowModal()
        dialog.Destroy()


class CollectionsDataSet(ceDatabase.DataSet):
    tableName = "Collections"
    attrNames = """collectionId causeId dateCollected reconciled description
            chequeAmount cashAmount"""
    retrievalAttrNames = "depositId"
    pkAttrNames = "collectionId"

    def _GetSqlForRetrieve(self):
        return """
                select
                    CollectionId,
                    CauseId,
                    DateCollected,
                    Reconciled,
                    Description,
                    ( select sum(ChequeAmount)
                      from CollectionAmounts
                      where CollectionId = c.CollectionId
                    ),
                    ( select sum(CashAmount)
                      from CollectionAmounts
                      where CollectionId = c.CollectionId
                    )
                from Collections c
                where DepositId = ?"""


class ChequesPanel(SubPanel):
    listClassName = "ChequesList"
    editDialogName = "EditDialogs.Cheques.Dialog"
    settingsName = "ChequesColumnWidths"
    labelText = "Cheques"

    def GetEditWindow(self, item = None):
        editWindow = super(ChequesPanel, self).GetEditWindow(item)
        if editWindow.dataSet.rows[0].causeId is not None:
            return editWindow
        editWindow.Destroy()


class ChequesList(ceGUI.DataList):
    dataSetClassName = "ChequesDataSet"

    def _CreateContextMenu(self):
        super(ChequesList, self)._CreateContextMenu()
        self.menu.AddSeparator()
        self.printMenuItem = self.menu.AddEntry(self, "Print Letter...",
                method = self.OnPrintLetter, passEvent = False)

    def OnContextMenu(self):
        enabled = (len(self.GetSelectedItems()) == 1)
        self.printMenuItem.Enable(enabled)
        super(ChequesList, self).OnContextMenu()

    def OnCreate(self):
        self.AddColumn("chequeNumber", "Number", 75)
        self.AddColumn("causeId", "Cause", 225, cls = Common.CauseColumn)
        self.AddColumn("amount", "Amount", cls = Common.AmountColumn,
                justification = wx.LIST_FORMAT_RIGHT)

    def OnPrintLetter(self):
        cheque = self.GetSelectedItem()
        cls = ceGUI.GetModuleItem("ReportDefs.ChequeLetter", "Report")
        report = cls()
        report.Preview([cheque])


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

    def DeleteRowInDatabase(self, cursor, row):
        cursor.execute("""
                insert into UnremittedAmounts
                (CollectionId, CauseId)
                select
                  CollectionId,
                  CauseId
                from ChequeAmounts
                where ChequeId = ?""",
                row.chequeId)
        cursor.execute("""
                delete from ChequeAmounts
                where ChequeId = ?""",
                row.chequeId)
        cursor.execute("""
                delete from Cheques
                where ChequeId = ?""",
                row.chequeId)


class DateColumn(ceGUI.ListDateColumn):
    dateFormat = "%b/%d/%Y (%a)"

