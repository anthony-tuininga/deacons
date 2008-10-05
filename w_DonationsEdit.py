"""
Dialog for editing donations.
"""

from __future__ import with_statement

import ceDatabase
import ceGUI
import decimal
import wx

import Common

class Dialog(Common.DonationsDialog):

    def _RowIsEmpty(self, row):
        return row.donatorId is None and row.amount == 0

    def OnCreate(self):
        parent = self.GetParent()
        self.collection = parent.list.GetSelectedItem()
        self.grid = Grid(self)
        title = "Edit Donations - %s" % \
                self.collection.dateCollected.strftime("%A, %B %d, %Y")
        self.SetTitle(title)
        super(Dialog, self).OnCreate()
        self.grid.Retrieve()
        if len(self.grid.table.rowHandles) == 0:
            self.grid.InsertRows(0)


class Grid(ceGUI.Grid):
    sortOnRetrieve = False

    def _CreateContextMenu(self):
        super(Grid, self)._CreateContextMenu()
        self.menu.AddSeparator()
        self.splitMenuItem = self.menu.AddEntry(self, "Split\tCtrl-T",
                method = self.OnSplit, passEvent = False)

    def _GetAccelerators(self):
        accelerators = super(Grid, self)._GetAccelerators()
        accelerators.append((wx.ACCEL_CTRL, ord('T'),
                self.splitMenuItem.GetId()))
        return accelerators

    def _GetTable(self):
        parent = self.GetParent()
        self.collection = parent.collection
        dataSet = DataSet(self.config.connection, parent.collection)
        return Table(dataSet)

    def InsertRows(self, pos, numRows = 1):
        super(Grid, self).InsertRows(pos, numRows)
        if len(self.table.rowHandles) == 1:
            targetRow = self.table.dataSet.rows[0]
            targetRow.causeId = self.collection.causeId
        elif pos > 0 and pos < len(self.table.rowHandles):
            sourceHandle = self.table.rowHandles[pos - 1]
            targetHandle = self.table.rowHandles[pos]
            sourceRow = self.table.dataSet.rows[sourceHandle]
            targetRow = self.table.dataSet.rows[targetHandle]
            targetRow.causeId = sourceRow.causeId
            targetRow.cash = sourceRow.cash

    def DeleteRows(self, row, numRows = 1):
        super(Grid, self).DeleteRows(row, numRows)
        self.Update()

    def OnCreate(self):
        self.AddColumn("assignedNumber", "Number", 70,
                cls = GridColumnAssignedNumber)
        self.AddColumn("donatorId", "Name", 220, cls = GridColumnName,
                required = True)
        self.AddColumn("causeId", "Cause", 175, cls = GridColumnCause,
                required = True)
        self.AddColumn("cash", "Cash", 65, cls = ceGUI.GridColumnBool)
        self.AddColumn("amount", "Amount", cls = Common.GridColumnAmount)

    def OnContextMenu(self):
        self.splitMenuItem.Enable(self.contextRow != wx.NOT_FOUND)
        super(Grid, self).OnContextMenu()

    def OnSplit(self):
        if self.contextRow is None:
            rowNum = self.GetGridCursorRow()
        else:
            rowNum = self.contextRow
        if rowNum == wx.NOT_FOUND:
            return
        handle = self.table.rowHandles[rowNum]
        row = self.table.dataSet.rows[handle]
        if row.splitDonation is None:
            dataSet = self.table.dataSet.splitDonationsDataSet
            splitDonation = dataSet.rowClass.New()
            splitDonation.donatorId = row.donatorId
            splitDonation.collectionId = row.collectionId
            splitDonation.claimYear = row.claimYear
            splitDonation.donations = []
            splitDonation.amount = decimal.Decimal(0)
            with self.config.connection:
                cursor = self.config.connection.cursor()
                dataSet.InsertRowInDatabase(cursor, splitDonation)
                if row.donationId is not None:
                    newRow = row.Copy()
                    newRow.splitDonation = None
                    newRow.splitDonationId = splitDonation.splitDonationId
                    splitDonation.donations.append(newRow)
                    splitDonation.amount = newRow.amount
                    self.table.dataSet.UpdateRowInDatabase(cursor, newRow,
                            row)
            self.table.dataSet.ClearChanges()
            row.splitDonation = splitDonation
        parent = self.GetParent()
        dialog = parent.OpenWindow("w_SplitDonationsEdit.Dialog")
        dialog.Setup(self.collection, row.splitDonation,
                self.table.dataSet.causes)
        dialog.ShowModal()
        row.amount = row.splitDonation.amount
        self.Refresh()


class Table(ceGUI.GridTable):

    def GetAttr(self, rowIndex, colIndex, kind):
        if rowIndex < len(self.rowHandles) and colIndex < len(self.columns):
            handle = self.rowHandles[rowIndex]
            row = self.dataSet.rows[handle]
            column = self.columns[colIndex]
            if row.splitDonation is not None \
                    and column.attrName in ("causeId", "cash", "amount"):
                attr = column.attr.Clone()
                attr.SetReadOnly()
                return attr
        return super(Table, self).GetAttr(rowIndex, colIndex, kind)


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
        rowIndex = grid.GetGridCursorRow()
        grid.SetGridCursor(rowIndex, 3)
        grid.Refresh()
        return True


class GridColumnCause(Common.GridColumnCause):

    def SetValue(self, grid, dataSet, rowHandle, row, rawValue):
        if row.splitDonation is None and rawValue.startswith("-"):
            grid.OnSplit()
        else:
            super(GridColumnCause, self).SetValue(grid, dataSet, rowHandle,
                    row, rawValue)


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
        rowIndex = grid.GetGridCursorRow()
        grid.SetGridCursor(rowIndex, 3)
        grid.Refresh()
        return True


class SplitDonationsDataSet(ceDatabase.DataSet):
    tableName = "SplitDonations"
    attrNames = "splitDonationId collectionId donatorId"
    extraAttrNames = "donations amount claimYear"
    pkAttrNames = "splitDonationId"
    retrievalAttrNames = "collectionId"
    sortByAttrNames = "splitDonationId"
    pkSequenceName = "SplitDonationId_s"
    pkIsGenerated = True

    def _GetRows(self, collectionId):
        rows = super(SplitDonationsDataSet, self)._GetRows(collectionId)
        for row in rows:
            row.claimYear = self.contextItem.dateCollected.year
            row.amount = decimal.Decimal(0)
            row.donations = []
        return rows


class DataSet(Common.DonationsDataSet):

    def __Setup(self):
        cursor = self.connection.cursor()
        cursor.execute("""
                select CauseId
                from CollectionCauses
                where CollectionId = ?""",
                self.contextItem.collectionId)
        self.causes = dict.fromkeys(i for i, in cursor)
        self.splitDonationsDataSet = SplitDonationsDataSet(self.connection,
                self.contextItem)
        self.splitDonationsDataSet.Retrieve()

    def _GenerateRow(self, splitDonation):
        generatedRow = self.rowClass.New()
        generatedRow.amount = splitDonation.amount
        generatedRow.donatorId = splitDonation.donatorId
        generatedRow.claimYear = splitDonation.claimYear
        generatedRow.collectionId = splitDonation.collectionId
        generatedRow.splitDonationId = splitDonation.splitDonationId
        generatedRow.splitDonation = splitDonation
        return generatedRow

    def _GetRows(self, collectionId):
        self.__Setup()
        rows = []
        splitDonations = {}
        for row in self.splitDonationsDataSet.rows.itervalues():
            splitDonations[row.splitDonationId] = row
        generatedRows = {}
        rawRows = super(DataSet, self)._GetRows(collectionId)
        for row in rawRows:
            if row.splitDonationId is None:
                rows.append(row)
            else:
                splitDonation = splitDonations[row.splitDonationId]
                generatedRow = generatedRows.get(row.splitDonationId)
                if generatedRow is None:
                    generatedRow = self._GenerateRow(splitDonation)
                    rows.append(generatedRow)
                    generatedRows[row.splitDonationId] = generatedRow
                splitDonation.amount += row.amount
                splitDonation.donations.append(row)
                generatedRow.amount = splitDonation.amount
        for splitDonation in splitDonations.itervalues():
            if splitDonation.splitDonationId in generatedRows:
                continue
            generatedRow = self._GenerateRow(splitDonation)
            rows.append(generatedRow)
        return rows

    def DeleteRowInDatabase(self, cursor, row):
        if row.splitDonation is None:
            super(DataSet, self).DeleteRowInDatabase(cursor, row)
        else:
            for subRow in row.splitDonation.donations:
                super(DataSet, self).DeleteRowInDatabase(cursor, subRow)
            self.splitDonationsDataSet.DeleteRowInDatabase(cursor,
                    row.splitDonation)

    def UpdateRowInDatabase(self, cursor, row, origRow):
        if row.splitDonation is None:
            super(DataSet, self).UpdateRowInDatabase(cursor, row, origRow)
        else:
            for subRow in row.splitDonation.donations:
                origSubRow = subRow.Copy()
                subRow.donatorId = row.donatorId
                super(DataSet, self).UpdateRowInDatabase(cursor, subRow,
                        origSubRow)
            self.splitDonationsDataSet.UpdateRowInDatabase(cursor, row,
                    origRow)

