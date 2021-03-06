"""
Panel which displays donations and enables editing of them.
"""

import ceGUI

import Common
import Models

class Panel(Common.BasePanel):

    def GetBaseRows(self):
        return self.grid.dataSet.rowClass.GetRows(self.config.dataSource,
                year = self.config.year)

    def OnCreateFilterArgs(self):
        self.CreateDateDepositedFilterArg()
        self.CreateDateCollectedFilterArg()
        self.CreateCauseFilterArg()

    def OnPopulateBaseRows(self, rows):
        self.SetDateDepositedChoices(rows)
        self.SetDateCollectedChoices(rows)
        self.SetCauseChoices(rows)


class Grid(Common.BaseGrid):

    def OnCreate(self):
        super(Grid, self).OnCreate()
        self.dateDepositedColumn = self.AddColumn("dateDeposited", "Deposited",
                defaultWidth = 100, cls = ColumnDateAutoFill, required = True)
        self.dateCollectedColumn = self.AddColumn("dateCollected",
                "Collected", defaultWidth = 100, cls = ColumnDateAutoFill,
                required = True)
        self.AddColumn("cash", "Cash", defaultWidth = 100,
                cls = ceGUI.ColumnBool)
        self.AddColumn("causeId", "Cause", defaultWidth = 200,
                cls = Common.ColumnCauseDescription, required = True)
        self.AddColumn("donatorId", "Donator", defaultWidth = 300,
                cls = Common.ColumnDonatorName, required = True)
        self.AddColumn("amount", "Amount", defaultWidth = 200,
                cls = ceGUI.ColumnMoney, required = True)

    def OnInsertRow(self, row, choice):
        row.dateDeposited = self.dateDepositedColumn.lastValue
        row.dateCollected = self.dateCollectedColumn.lastValue

    def VerifyData(self):
        super(Grid, self).VerifyData()
        chequeDict = {}
        dataSet = self.table.dataSet
        for handle, row in dataSet.insertedRows.items():
            if row.cash:
                continue
            key = (row.dateCollected, row.dateDeposited, row.donatorId)
            causeIds = chequeDict.setdefault(key, [])
            if row.causeId in causeIds:
                rowIndex = self.table.rowHandles.index(handle)
                self.SetGridCursor(rowIndex, 3)
                self.MakeCellVisible(rowIndex, 3)
                raise Exception("Duplicated cause for split cheque!")
            causeIds.append(row.causeId)


class DataSet(ceGUI.DataSet):
    rowClass = Models.Donations
    updateTableName = "Donations"
    pkSequenceName = "DonationId_s"
    pkIsGenerated = True
    insertAttrNames = "dateCollected dateDeposited donatorId cash"
    updateAttrNames = "dateCollected dateDeposited donatorId cash"

    def _GetRows(self, rows, datesDeposited, datesCollected, causeIds):
        if datesDeposited:
            rows = [r for r in rows if r.dateDeposited in datesDeposited]
        if datesCollected:
            rows = [r for r in rows if r.dateCollected in datesCollected]
        if causeIds:
            rows = [r for r in rows if r.causeId in causeIds]
        return rows

    def _InsertRowsInDatabase(self, transaction):
        chequeDict = {}
        for row in self.insertedRows.values():
            donationItem = None
            if not row.cash:
                key = (row.dateCollected, row.dateDeposited, row.donatorId)
                donationItem = chequeDict.get(key)
            if donationItem is None:
                donationItem = self.InsertRowInDatabase(transaction, row)
                if not row.cash:
                    chequeDict[key] = donationItem
            setValues = dict(causeId = row.causeId, amount = row.amount,
                    donationId = None)
            transaction.AddItem(tableName = "DonationComponents",
                    setValues = setValues, referencedItems = [donationItem],
                    fkArgs = ["donationId"])

    def UpdateRowInDatabase(self, transaction, row, origRow):
        super(DataSet, self).UpdateRowInDatabase(transaction, row, origRow)
        setValues = dict(causeId = row.causeId, amount = row.amount)
        transaction.AddItem(tableName = "DonationComponents",
                setValues = setValues,
                conditions = dict(donationId = row.donationId))


class ColumnDateAutoFill(ceGUI.ColumnDate):
    lastValue = None

    def VerifyValueOnChange(self, row, rawValue):
        self.lastValue = \
                super(ColumnDateAutoFill, self).VerifyValueOnChange(row,
                        rawValue)
        return self.lastValue

