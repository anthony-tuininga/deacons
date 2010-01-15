"""
Dialog for editing years.
"""

import ceDatabase
import ceGUI
import cx_Logging
import wx

import Common

class Dialog(ceGUI.EditDialog):
    title = "Edit Year"
    defaultWidth = 280


class Panel(ceGUI.DataEditPanel):

    def OnCreate(self):
        parent = self.GetParent()
        if parent.parentItem is not None:
            style = wx.TE_READONLY
        else:
            style = 0
        self.AddColumn("year", "Year:",
                self.AddIntegerField(style = style), required = True)
        self.AddColumn("budgetAmount", "Budget:", Common.AmountField(self),
                required = True)
        self.AddColumn("promptForReceiptGeneration", "Receipts Prompt?",
                self.AddCheckBox())
        self.AddColumn("receiptsIssued", "Receipts Issued?",
                self.AddCheckBox())


class DataSet(ceDatabase.DataSet):
    tableName = "Years"
    attrNames = "year budgetAmount promptForReceiptGeneration receiptsIssued"
    charBooleanAttrNames = "promptForReceiptGeneration receiptsIssued"
    retrievalAttrNames = pkAttrNames = "year"

    def InsertRowInDatabase(self, cursor, row):
        cursor.execute("""
                select max(Year)
                from Years
                where Year < ?""",
                row.year)
        fetchedRow = cursor.fetchone()
        copyFromYear = fetchedRow and fetchedRow[0]
        super(DataSet, self).InsertRowInDatabase(cursor, row)
        if copyFromYear is not None:
            cx_Logging.Info("Copying causes and donators from year %s",
                    copyFromYear)
            cursor.execute("""
                    insert into CausesForYear (
                        CauseId,
                        Year,
                        Deductible
                    )
                    select
                        CauseId,
                        ?,
                        Deductible
                    from CausesForYear
                    where Year = ?""",
                    row.year, copyFromYear)
            cursor.execute("""
                    insert into DonatorsForYear (
                        DonatorId,
                        Year,
                        AssignedNumber
                    )
                    select
                        DonatorId,
                        ?,
                        AssignedNumber
                    from DonatorsForYear
                    where Year = ?""",
                    row.year, copyFromYear)

