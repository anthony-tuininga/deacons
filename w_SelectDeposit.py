import ceDatabase
import ceGUI

class Dialog(ceGUI.SelectionListDialog):
    title = "Select Deposit"

    def OnCreate(self):
        super(Dialog, self).OnCreate()
        self.Retrieve()


class List(ceGUI.List):
    singleSelection = True
    sortOnRetrieve = False

    def OnCreate(self):
        self.AddColumn("dateDeposited", "Date", cls = DateColumn)


class DataSet(ceDatabase.DataSet):
    tableName = "Deposits"
    attrNames = "depositId dateDeposited"
    sortByAttrNames = "dateDeposited"
    pkAttrNames = "depositId"

    def _GetSqlForRetrieve(self):
        sql = super(DataSet, self)._GetSqlForRetrieve()
        return sql + " desc"


class DateColumn(ceGUI.ListDateColumn):
    dateFormat = "%a, %b %d/%y"

