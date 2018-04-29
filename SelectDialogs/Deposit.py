import ceGUI

import Models

class Dialog(ceGUI.SelectionListDialog):
    title = "Select Deposit"
    defaultSize = (350, 475)


class List(ceGUI.List):
    singleSelection = True
    sortOnRetrieve = False

    def OnCreate(self):
        self.AddColumn("dateDeposited", "Date", cls = DateColumn)


class DataSet(ceGUI.DataSet):
    rowClass = Models.Deposits
    retrievalAttrNames = "year"


class DateColumn(ceGUI.ListDateColumn):
    dateFormat = "%a, %b %d, %Y"

