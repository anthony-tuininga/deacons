"""
Panel displaying information about years.
"""

import ceGUI
import cx_Logging
import decimal

import Common
import Models

class Panel(Common.BasePanel):
    pass


class Grid(Common.BaseGrid):

    def OnCreate(self):
        super(Grid, self).OnCreate()
        self.AddColumn("year", "Year", defaultWith = 50)
        self.AddColumn("budgetAmount", "Budget Amount",
                cls = ceGUI.ColumnMoney, defaultWidth = 175)
        self.AddColumn("receiptsIssued", "Receipts Issued",
                cls = ceGUI.ColumnBool, defaultWidth = 200)
        self.AddColumn("notes", "Notes", defaultWidth = 200)


class DataSet(ceGUI.DataSet):
    rowClass = Models.Years

    def _OnInsertRow(self, row, choice):
        row.budgetAmount = decimal.Decimal(0)
        row.receiptsIssued = False

    def InsertRowInDatabase(self, transaction, row):
        cursor = self.dataSource.connection.cursor()
        cursor.execute("""
                select max(Year)
                from Years
                where Year < ?""",
                row.year)
        fetchedRow = cursor.fetchone()
        super(DataSet, self).InsertRowInDatabase(transaction, row)
        if fetchedRow is not None:
            copyFromYear, = fetchedRow
            cx_Logging.Info("Copying causes and donators from year %s",
                    copyFromYear)
            for cause in Models.Causes.GetRows(self.dataSource,
                    year = copyFromYear):
                setValues = dict(year = row.year,
                        description = cause.description,
                        deductible = cause.deductible,
                        reported = cause.reported,
                        notes = cause.notes,
                        donationAccountCode = cause.donationAccountCode,
                        looseCashAccountCode = cause.looseCashAccountCode)
                transaction.AddItem(tableName = Models.Causes.tableName,
                        pkAttrName = Models.Causes.pkAttrNames[0],
                        pkSequenceName = "CauseId_s", setValues = setValues)
            for donator in Models.Donators.GetRows(self.dataSource,
                    year = copyFromYear):
                setValues = dict(year = row.year,
                        surname = donator.surname,
                        givenNames = donator.givenNames,
                        assignedNumber = donator.assignedNumber,
                        address = donator.address)
                transaction.AddItem(tableName = Models.Donators.tableName,
                        pkAttrName = Models.Donators.pkAttrNames[0],
                        pkSequenceName = "DonatorId_s", setValues = setValues)

