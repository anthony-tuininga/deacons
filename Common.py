"""
Commonly defined items.
"""

import ceDatabase
import ceGUI
import cx_Exceptions
import decimal
import wx

import Models

class BasePanel(ceGUI.DataGridPanel):

    def CreateCauseFilterArg(self):
        self.causeFilterArg = ceGUI.FilterArgChoiceMultiple(self, "causeId",
                "Cause:", size = (300, -1))

    def CreateDateCollectedFilterArg(self):
        self.dateCollectedFilterArg = ceGUI.FilterArgChoiceMultiple(self,
                "dateCollected", "Date Collected:", size = (125, -1))

    def CreateDateDepositedFilterArg(self):
        self.dateDepositedFilterArg = ceGUI.FilterArgChoiceMultiple(self,
                "dateDeposited", "Date Deposited:", size = (125, -1))

    def GetYear(self):
        topWindow = ceGUI.AppTopWindow()
        return topWindow.year

    def OnYearChanged(self):
        self.Retrieve(refresh = True)

    def SetCauseChoices(self, rows):
        causeIdDict = dict.fromkeys(r.causeId for r in rows)
        causes = [c for c in self.config.GetCachedRows(Models.Causes) \
                if c.causeId in causeIdDict]
        causes.sort(key = lambda x: x.description.upper())
        choices = [(c.causeId, c.description) for c in causes]
        choices.insert(0, (None, "(Any)"))
        self.causeFilterArg.SetChoices(choices)

    def SetDateCollectedChoices(self, rows):
        datesCollected = list(dict.fromkeys(r.dateCollected for r in rows))
        datesCollected.sort()
        choices = [(d, d.strftime("%Y/%m/%d")) for d in datesCollected]
        choices.insert(0, (None, "(Any)"))
        self.dateCollectedFilterArg.SetChoices(choices)

    def SetDateDepositedChoices(self, rows):
        datesDeposited = list(dict.fromkeys(r.dateDeposited for r in rows))
        datesDeposited.sort()
        choices = [(d, d.strftime("%Y/%m/%d")) for d in datesDeposited]
        choices.insert(0, (None, "(Any)"))
        self.dateDepositedFilterArg.SetChoices(choices)


class BaseGrid(ceGUI.DataGrid):

    def OnCreate(self):
        self.GetParent().BindEvent(self, wx.grid.EVT_GRID_SELECT_CELL,
                self.OnCellSelected)
        self.SetTabBehaviour(wx.grid.Grid.Tab_Wrap)

    def OnCellSelected(self, event):
        self.ForceRefresh()
        event.Skip()


class ColumnCauseDescription(ceGUI.Column):

    def GetNativeValue(self, row):
        if row.causeId is not None:
            cause = self.config.GetCachedRowByPK(Models.Causes,
                    row.causeId)
            return cause.description

    def GetPossibleCauses(self, text):
        return [r for r in self.config.GetCachedRows(Models.Causes) \
                if r.year == self.config.year \
                and r.searchDescription.startswith(text)]

    def VerifyValueOnChange(self, row, rawValue):
        if rawValue:
            causes = self.GetPossibleCauses(rawValue.upper())
            if len(causes) == 0:
                message = "'%s' is not a valid cause." % rawValue
                raise ceGUI.InvalidValueEntered(message)
            elif len(causes) == 1:
                return causes[0].causeId
            parent = ceGUI.AppTopWindow()
            with parent.OpenWindow("SelectDialogs.Cause.Dialog") as dialog:
                dialog.Retrieve(causes)
                if dialog.ShowModalOk():
                    cause = dialog.GetSelectedItem()
                    return cause.causeId
                return getattr(row, self.attrName)


class ColumnDonatorName(ceGUI.Column):

    def GetNativeValue(self, row):
        if row.donatorId is not None:
            donator = self.config.GetCachedRowByPK(Models.Donators,
                    row.donatorId)
            if donator.assignedNumber is not None:
                return f"{donator.name} ({donator.assignedNumber})"
            return donator.name

    def VerifyValueOnChange(self, row, rawValue):
        if rawValue:
            rows = [r for r in self.config.GetCachedRows(Models.Donators) \
                    if r.year == self.config.year]
            if rawValue.isdigit():
                searchValue = int(rawValue)
                donators = [r for r in rows if r.assignedNumber == searchValue]
                if len(donators) == 1:
                    return donators[0].donatorId
            searchValue = rawValue.upper()
            donators = [r for r in rows if searchValue in r.searchName]
            if len(donators) == 0:
                message = "'%s' is not a valid donator name or number." % \
                        rawValue
                raise ceGUI.InvalidValueEntered(message)
            elif len(donators) == 1:
                return donators[0].donatorId
            parent = ceGUI.AppTopWindow()
            with parent.OpenWindow("SelectDialogs.Donator.Dialog") as dialog:
                dialog.Retrieve(donators)
                if dialog.ShowModalOk():
                    donator = dialog.GetSelectedItem()
                    return donator.donatorId
                return getattr(row, self.attrName)

