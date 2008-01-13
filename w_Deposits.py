import ceDatabase
import ceGUI

class EditWindow(ceGUI.GridEditWindow):
    title = "Deposits"

    def OnCreate(self):
        self.AddSubWindow(CollectionsSubWindow)
        self.AddSubWindow(SummarySubWindow)
        self.AddSubWindow(ChequesSubWindow)
        self.AddSubWindow(TreasurerSubWindow)
        self.AddSubWindow(ChequeReportSubWindow)


class Grid(ceGUI.Grid):
    
    def OnCreate(self):
        self.AddColumn(ceGUI.GridColumnStr, "Date", "dateDeposited")


class DataSet(ceDatabase.DataSet):
    tableName = "Deposits"
    attrNames = "depositId dateDeposited"
    pkAttrNames = "depositId"
    sortByAttrNames = "dateDeposited"
    pkIsGenerated = True
    pkSequenceName = "DepositId_s"


class ChequeReportSubWindow(ceGUI.SubWindow):
    childWindowName = "w_ChequeReport.EditWindow"
    label = "Chq Report..."


class ChequesSubWindow(ceGUI.SubWindow):
    childWindowName = "w_Cheques.EditWindow"
    label = "Summary..."


class CollectionsSubWindow(ceGUI.SubWindow):
    childWindowName = "w_DepositCollections.EditWindow"
    label = "Collections..."


class SummarySubWindow(ceGUI.SubWindow):
    childWindowName = "w_DepositSummary.EditWindow"
    label = "Summary..."


class TreasurerSubWindow(ceGUI.SubWindow):
    childWindowName = "w_TreasurerSummary.EditWindow"
    label = "Treasurer..."

