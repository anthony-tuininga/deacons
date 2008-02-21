"""
Dialog for editing donations.
"""

import ceDatabase
import ceGUI
import decimal
import wx

import Common

class Dialog(ceGUI.StandardDialog):

    def OnCreate(self):
        self.grid = Grid(self)
        parent = self.GetParent()
        self.collection = parent.list.contextItem
        title = "Edit Donations - %s" % \
                self.collection.dateCollected.strftime("%A, %B %d, %Y")
        self.SetTitle(title)
        self.grid.Retrieve(self.collection)
        self.grid.SetFocus()
        self.grid.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)

    def OnKeyDown(self, event):
        if event.GetKeyCode() != wx.WXK_TAB:
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
        self.grid.Update()

    def RestoreSettings(self):
        self.grid.RestoreColumnWidths()

    def SaveSettings(self):
        self.grid.SaveColumnWidths()


class Grid(ceGUI.Grid):

    def OnCreate(self):
        self.AddColumn("assignedNumber", "Number", 70,
                cls = GridColumnAssignedNumber)
        self.AddColumn("donatorId", "Name", 220, cls = GridColumnName)
        self.AddColumn("causeId", "Cause", 175, cls = GridColumnCause)
        self.AddColumn("cash", "Cash", 65, cls = ceGUI.GridColumnBool)
        self.AddColumn("amount", "Amount", cls = GridColumnAmount)


class GridColumnAmount(ceGUI.GridColumn):
    defaultHorizontalAlignment = wx.ALIGN_RIGHT

    def GetValue(self, row):
        return Common.FormattedAmount(row.amount)

    def SetValue(self, grid, dataSet, rowHandle, row, rawValue):
        massagedValue = rawValue.replace("$", "").replace(",", "")
        value = decimal.Decimal(massagedValue)
        dataSet.SetValue(rowHandle, self.attrName, value)
        return True


class GridColumnAssignedNumber(ceGUI.GridColumnInt):

    def GetSortValue(self, row):
        if row.donatorId is not None:
            cache = self.config.cache
            donator = cache.DonatorForId(row.donatorId)
            return cache.AssignedNumberForDonator(donator, row.claimYear)

    def GetValue(self, row):
        if row.donatorId is not None:
            cache = self.config.cache
            donator = cache.DonatorForId(row.donatorId)
            num = cache.AssignedNumberForDonator(donator, row.claimYear)
            if num is not None:
                return str(num)
        return ""

    def SetValue(self, grid, dataSet, rowHandle, row, rawValue):
        if row.donatorId is None:
            prevValue = None
        else:
            donator = grid.config.cache.DonatorForId(row.donatorId)
            prevValue = grid.config.cache.AssignedNumberForDonator(donator,
                    row.claimYear)
        if not rawValue:
            if prevValue:
                dataSet.SetValue(rowHandle, "donatorId", None)
                grid.Refresh()
            return True
        newDonator = grid.config.cache.DonatorForAssignedNumber(row.claimYear,
                int(rawValue))
        if newDonator is None:
            return False
        dataSet.SetValue(rowHandle, "donatorId", newDonator.donatorId)
        grid.Refresh()
        return True


class GridColumnCause(ceGUI.GridColumn):

    def GetSortValue(self, row):
        if row.causeId is not None:
            cause = self.config.cache.CauseForId(row.causeId)
            return cause.description.upper()

    def GetValue(self, row):
        if row.causeId is None:
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
                if c.active and c.searchDescription.startswith(searchValue)]
        selectedCause = None
        if len(causes) == 1:
            selectedCause, = causes
        elif causes:
            parent = grid.GetParent()
            dialog = parent.OpenWindow("w_SelectCause.Dialog")
            dialog.Retrieve(causes)
            if dialog.ShowModal() == wx.ID_OK:
                selectedCause = dialog.GetSelectedItem()
            dialog.Destroy()
        if selectedCause is None:
            return False
        dataSet.SetValue(rowHandle, self.attrName, selectedCause.causeId)
        return True


class GridColumnName(ceGUI.GridColumn):

    def GetSortValue(self, row):
        if row.donatorId is not None:
            donator = self.config.cache.DonatorForId(row.donatorId)
            return donator.reversedName.upper()

    def GetValue(self, row):
        if row.donatorId is None:
            return ""
        donator = self.config.cache.DonatorForId(row.donatorId)
        return donator.reversedName

    def SetValue(self, grid, dataSet, rowHandle, row, rawValue):
        if row.donatorId is not None:
            donator = grid.config.cache.DonatorForId(row.donatorId)
            if rawValue == donator.reversedName:
                return True
        if not rawValue:
            dataSet.SetValue(rowHandle, self.attrName, None)
            grid.Refresh()
            return True
        searchValue = rawValue.upper()
        donators = [d for d in grid.config.cache.Donators() \
                if d.active and d.searchReversedName.startswith(searchValue)]
        selectedDonator = None
        if len(donators) == 1:
            selectedDonator, = donators
        elif donators:
            parent = grid.GetParent()
            dialog = parent.OpenWindow("w_SelectDonator.Dialog")
            dialog.Retrieve(donators)
            if dialog.ShowModal() == wx.ID_OK:
                selectedDonator = dialog.GetSelectedItem()
            dialog.Destroy()
        if selectedDonator is None:
            return False
        dataSet.SetValue(rowHandle, self.attrName, selectedDonator.donatorId)
        grid.Refresh()
        return True


class DataSet(ceDatabase.DataSet):
    tableName = "Donations"
    attrNames = """donationId causeId claimYear amount cash donatorId
            splitDonationId"""
    charBooleanAttrNames = "cash"
    pkAttrNames = "donationId"
    retrievalAttrNames = "collectionId"
    pkSequenceName = "DonationId_s"
    pkIsGenerated = True

    def _GetRows(self, collection):
        self.collection = collection
        cursor = self.connection.cursor()
        cursor.execute("""
                select CauseId
                from CollectionCauses
                where CollectionId = ?""",
                collection.collectionId)
        self.causes = dict.fromkeys(i for i, in cursor)
        rows = super(DataSet, self)._GetRows(collection.collectionId)
        for row in rows:
            row.amount = decimal.Decimal(str(row.amount))
        return rows

    def __EnsureCause(self, cursor, row):
        if row.causeId not in self.causes:
            cursor.execute("""
                    insert into CollectionCauses
                    (CollectionId, CauseId)
                    values (?, ?)""",
                    self.collection.collectionId, row.causeId)
            self.causes[row.causeId] = None

    def _OnInsertRow(self, row, choice):
        row.amount = decimal.Decimal("0.00")
        row.claimYear = self.collection.dateCollected.year
        row.cash = False

    def InsertRowInDatabase(self, cursor, row):
        self.__EnsureCause(cursor, row)
        super(DataSet, self).InsertRowInDatabase(cursor, row)

    def UpdateRowInDatabase(self, cursor, row, origRow):
        self.__EnsureCause(cursor, row)
        super(DataSet, self).UpdateRowInDatabase(cursor, row, origRow)

