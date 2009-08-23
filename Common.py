"""
Commonly defined items.
"""

import ceDatabase
import ceGUI
import cx_Exceptions
import decimal
import wx

def FormattedAmount(value):
    if value is None:
        return "$0.00"
    if value < 1000:
        return "$%.2f" % value
    thousands = int(str(int(value))[:-3])
    number = "%.2f" % (value - 1000 * (thousands - 1))
    return "$%s,%s" % (str(thousands), number[1:])


class AmountColumn(ceGUI.ListColumn):

    def GetValue(self, row):
        value = getattr(row, self.attrName)
        return FormattedAmount(value)


class BooleanColumn(ceGUI.ListColumn):

    def GetValue(self, row):
        value = getattr(row, self.attrName)
        if value:
            return "Yes"
        return "No"


class CauseColumn(ceGUI.ListColumn):

    def GetValue(self, row):
        causeId = getattr(row, self.attrName)
        if causeId is not None:
            cause = self.config.cache.CauseForId(causeId)
            return cause.description

    def GetSortValue(self, row):
        causeId = getattr(row, self.attrName)
        if causeId is not None:
            cause = self.config.cache.CauseForId(causeId)
            return cause.description.upper()


class GivenNamesColumn(ceGUI.ListColumn):

    def GetValue(self, row):
        if row.donatorId is not None:
            donator = self.config.cache.DonatorForId(row.donatorId)
            return donator.givenNames

    def GetSortValue(self, row):
        if row.donatorId is not None:
            donator = self.config.cache.DonatorForId(row.donatorId)
            if donator.givenNames is not None:
                return donator.givenNames.upper()


class LastNameColumn(ceGUI.ListColumn):

    def GetValue(self, row):
        if row.donatorId is not None:
            donator = self.config.cache.DonatorForId(row.donatorId)
            return donator.lastName

    def GetSortValue(self, row):
        if row.donatorId is not None:
            donator = self.config.cache.DonatorForId(row.donatorId)
            return donator.lastName.upper()


class NameColumn(ceGUI.ListColumn):

    def GetValue(self, row):
        if row.donatorId is not None:
            donator = self.config.cache.DonatorForId(row.donatorId)
            return donator.name

    def GetSortValue(self, row):
        if row.donatorId is not None:
            donator = self.config.cache.DonatorForId(row.donatorId)
            return donator.name.upper()


class AmountField(ceGUI.TextField):

    def _Initialize(self):
        super(AmountField, self)._Initialize()
        ceGUI.EventHandler(self.GetParent(), self, wx.EVT_CHAR, self.OnChar,
                skipEvent = False)
                
    def GetValue(self):
        value = super(AmountField, self).GetValue()
        if value is not None:
            return decimal.Decimal(value.replace("$", "").replace(",", ""))
            
    def OnChar(self, event):
        key = event.GetKeyCode()
        if key in (wx.WXK_BACK, wx.WXK_DELETE) or key > 127:
            event.Skip()
        if key >= ord('0') and key <= ord('9'):
            event.Skip()
        if key == ord('$') or key == ord(','):
            event.Skip()
            
    def SetValue(self, value):
        if value is not None:
            value = FormattedAmount(value)
        super(AmountField, self).SetValue(value)


class Panel(ceGUI.Panel):

    def PrintReport(self, name, *args):
        cls = ceGUI.GetModuleItem(name, "Report")
        report = cls()
        report.Preview(args)


class DonationsDialog(ceGUI.StandardDialog):
    createCancelButton = False

    def OnCreate(self):
        self.grid.SetFocus()
        self.grid.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.BindEvent(self.grid, wx.grid.EVT_GRID_SELECT_CELL,
                self.OnSelectCell)

    def OnKeyDown(self, event):
        if event.GetKeyCode() not in (wx.WXK_TAB, wx.WXK_RETURN):
            event.Skip()
            return
        if event.ControlDown():
            event.Skip()
            return
        self.grid.DisableCellEditControl()
        shifted = event.ShiftDown()
        if shifted:
            success = self.grid.MoveCursorLeft(False)
        else:
            success = self.grid.MoveCursorRight(False)
        if not success:
            if shifted:
                newRow = self.grid.GetGridCursorRow() - 1
                if newRow >= 0:
                    colIndex = self.grid.GetNumberCols() - 1
                    self.grid.SetGridCursor(newRow, colIndex)
                    self.grid.MakeCellVisible(newRow, colIndex)
            else:
                newRow = self.grid.GetGridCursorRow() + 1
                if newRow < self.grid.GetNumberRows():
                    self.grid.SetGridCursor(newRow, 0)
                    self.grid.MakeCellVisible(newRow, 0)
                else:
                    self.grid.InsertRows(newRow)

    def OnLayout(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.grid, flag = wx.EXPAND | wx.ALL, proportion = 1,
                border = 5)
        return sizer

    def OnOk(self):
        row = self.grid.GetCurrentRow()
        if row is not None and self._RowIsEmpty(row):
            self.grid.DeleteRows(self.grid.GetGridCursorRow())
        self.grid.Update()

    def OnSelectCell(self, event):
        newRow = event.GetRow()
        origRow = self.grid.GetGridCursorRow()
        if newRow != origRow and origRow >= 0:
            self.grid.SaveEditControlValue()
            handle = self.grid.table.rowHandles[origRow]
            row = self.grid.table.dataSet.rows[handle]
            if self._RowIsEmpty(row):
                self.grid.DeleteRows(origRow)
                return
            for column in self.grid.table.columns:
                exc = column.VerifyValue(row)
                if exc is not None:
                    colIndex = self.grid.table.columns.index(column)
                    self.grid.SetGridCursor(origRow, colIndex)
                    self.grid.EnableCellEditControl()
                    raise exc
            self.grid.table.dataSet.UpdateSingleRow(handle)

    def RestoreSettings(self):
        self.grid.RestoreColumnWidths()

    def SaveSettings(self):
        self.grid.SaveColumnWidths()


class GridColumnAmount(ceGUI.GridColumn):
    defaultHorizontalAlignment = wx.ALIGN_RIGHT

    def GetValue(self, row):
        return FormattedAmount(row.amount)

    def SetValue(self, grid, dataSet, rowHandle, row, rawValue):
        massagedValue = rawValue.replace("$", "").replace(",", "")
        if not massagedValue:
            massagedValue = "0"
        value = decimal.Decimal(massagedValue)
        dataSet.SetValue(rowHandle, self.attrName, value)
        return True

    def VerifyValue(self, row):
        if row.amount == 0:
            return AmountCannotBeZero()


class GridColumnCause(ceGUI.GridColumn):

    def GetSortValue(self, row):
        if row.causeId is not None:
            cause = self.config.cache.CauseForId(row.causeId)
            return cause.description.upper()

    def GetValue(self, row):
        if row.splitDonation is not None:
            return "-- Split --"
        elif row.causeId is None:
            return ""
        cause = self.config.cache.CauseForId(row.causeId)
        return cause.description

    def SetValue(self, grid, dataSet, rowHandle, row, rawValue):
        if row.causeId is not None:
            cause = grid.config.cache.CauseForId(row.causeId)
            if rawValue == cause.description:
                return True
        if not rawValue:
            dataSet.SetValue(rowHandle, self.attrName, None)
            return True
        searchValue = rawValue.upper()
        causes = [c for c in grid.config.cache.Causes() \
                if c.isActive and c.searchDescription.startswith(searchValue)]
        selectedCause = None
        if len(causes) == 1:
            selectedCause, = causes
        elif causes:
            parent = grid.GetParent()
            dialog = parent.OpenWindow("SelectDialogs.Cause.Dialog")
            dialog.Retrieve(causes)
            if dialog.ShowModal() == wx.ID_OK:
                selectedCause = dialog.GetSelectedItem()
            dialog.Destroy()
        if selectedCause is None:
            return False
        dataSet.SetValue(rowHandle, self.attrName, selectedCause.causeId)
        return True

    def VerifyValue(self, row):
        if row.splitDonation is None:
            return super(GridColumnCause, self).VerifyValue(row)


class AmountCannotBeZero(cx_Exceptions.BaseException):
    message = "Amount cannot be zero."


class DonationsDataSet(ceDatabase.DataSet):
    tableName = "Donations"
    attrNames = """donationId causeId claimYear amount cash donatorId
            collectionId splitDonationId"""
    charBooleanAttrNames = "cash"
    extraAttrNames = "splitDonation"
    pkAttrNames = "donationId"
    retrievalAttrNames = "collectionId"
    sortByAttrNames = "donationId"
    pkSequenceName = "DonationId_s"
    pkIsGenerated = True

    def _GetRows(self, collectionId):
        rows = super(DonationsDataSet, self)._GetRows(collectionId)
        for row in rows:
            row.amount = decimal.Decimal(str(row.amount))
            row.splitDonation = None
        return rows

    def __EnsureCause(self, cursor, row):
        if row.causeId not in self.causes:
            cursor.execute("""
                    insert into CollectionCauses
                    (CollectionId, CauseId)
                    values (?, ?)""",
                    self.contextItem.collectionId, row.causeId)
            self.causes[row.causeId] = None
            app = wx.GetApp()
            cause = app.config.cache.CauseForId(row.causeId)
            if cause.address is not None:
                cursor.execute("""
                        insert into UnremittedAmounts
                        (CollectionId, CauseId)
                        values (?, ?)""",
                        self.contextItem.collectionId, row.causeId)

    def _OnInsertRow(self, row, choice):
        row.amount = decimal.Decimal("0.00")
        row.collectionId = self.contextItem.collectionId
        row.claimYear = self.contextItem.dateCollected.year
        row.splitDonation = None
        row.cash = False

    def InsertRowInDatabase(self, cursor, row):
        self.__EnsureCause(cursor, row)
        super(DonationsDataSet, self).InsertRowInDatabase(cursor, row)

    def UpdateRowInDatabase(self, cursor, row, origRow):
        self.__EnsureCause(cursor, row)
        super(DonationsDataSet, self).UpdateRowInDatabase(cursor, row,
                origRow)


class ReportBody(ceGUI.ReportBody):
    borderHeight = 14
    interColumnWidth = 12
    pointsPerLine = 42

    def __init__(self):
        super(ReportBody, self).__init__()
        self.font = wx.Font(25, wx.ROMAN, wx.NORMAL, wx.NORMAL)

    def BoxedHeight(self, numRows):
        return self.borderHeight * 2 + self.pointsPerLine * numRows


class TextReport(object):

    def __init__(self, cache):
        self.cache = cache
        self.connection = cache.connection

    def GetBudgetAmountForYear(self, year):
        cursor = self.connection.cursor()
        cursor.execute("""
                select BudgetAmount
                from Years
                where Year = ?""",
                year)
        row = cursor.fetchone()
        if row is None:
            return 0
        amount, = row
        return amount

