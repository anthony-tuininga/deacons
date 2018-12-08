"""
Print a report of the cheques, coin and cash deposited for a particular date.
"""

from . import BaseReport

import Models

class Report(BaseReport):
    minChequesPerColumn = 10
    maxChequesPerColumn = 45
    numChequeColumns = 8

    def __GetChequeColumns(self, dateDeposited):
        chequeColumns = []
        cheques = Models.DepositCheques.GetRows(self.config.dataSource,
                dateDeposited = dateDeposited)
        while cheques:
            column = ChequeColumn(cheques[0].dateCollected)
            for cheque in cheques:
                if cheque.dateCollected != column.dateCollected:
                    break
                column.amounts.append(cheque.amount)
                if len(column.amounts) == self.maxChequesPerColumn:
                    break
            cheques = cheques[column.numAmounts:]
            if len(column.amounts) < self.minChequesPerColumn \
                    and len(chequeColumns) > 0 \
                    and chequeColumns[-1].dateCollected == column.dateCollected:
                prevColumn = chequeColumns[-1]
                totalCheques = prevColumn.numAmounts + column.numAmounts
                numCheques = totalCheques // 2 + totalCheques % 2
                column.amounts = \
                        prevColumn.amounts[numCheques:] + column.amounts
                prevColumn.amounts = prevColumn.amounts[:numCheques]
            chequeColumns.append(column)
        while len(chequeColumns) < self.numChequeColumns:
            chequeColumns.append(ChequeColumn())
        return chequeColumns

    def __GetChequeRows(self, chequeColumns):
        maxNumAmounts = max(c.numAmounts for c in chequeColumns)
        chequeRows = []
        for ix in range(maxNumAmounts):
            row = ChequeRow()
            for column in chequeColumns:
                value = column.amounts[ix] if ix < column.numAmounts else None
                row.amounts.append(value)
            chequeRows.append(row)
        return chequeRows

    def GetCriteria(self, topWindow):
        with topWindow.OpenWindow("SelectDialogs.Deposit.Dialog") as dialog:
            dialog.Retrieve(self.config.year)
            if dialog.ShowModalOk():
                item = dialog.GetSelectedItem()
                return [item.dateDeposited]

    def Run(self, dateDeposited):
        coinGroup = CashGroup(True)
        cashGroup = CashGroup(False)
        cashDenominationDict = {}
        for row in Models.CashDenominations.GetRows(self.config.dataSource):
            group = coinGroup if row.coin else cashGroup
            cashDenomination = CashData(row)
            cashDenominationDict[row.cashDenominationId] = cashDenomination
            group.cashDenominations.append(cashDenomination)
        for row in Models.DepositCash.GetRows(self.config.dataSource,
                dateDeposited = dateDeposited):
            cashDenomination = cashDenominationDict[row.cashDenominationId]
            cashDenomination.quantity += row.quantity
        chequeColumns = self.__GetChequeColumns(dateDeposited)
        chequeRows = self.__GetChequeRows(chequeColumns)
        allCashGroups = [coinGroup, cashGroup]
        totals = Totals(allCashGroups, chequeColumns)
        self.config.GeneratePDF("DepositSummary.rml",
                cashGroups = allCashGroups, chequeRows = chequeRows,
                chequeColumns = chequeColumns, dateDeposited = dateDeposited,
                totals = totals)


class CashGroup(object):

    def __init__(self, coin):
        self.title = "Coin" if coin else "Cash"
        self.cashDenominations = []

    @property
    def totalAmount(self):
        return sum(d.value * d.quantity for d in self.cashDenominations)


class CashData(object):

    def __init__(self, cashDenomination):
        self.cashDenominationId = cashDenomination.cashDenominationId
        self.value = cashDenomination.value
        self.coin = cashDenomination.coin
        self.quantity = 0


class ChequeColumn(object):

    def __init__(self, dateCollected = None):
        self.dateCollected = dateCollected
        self.amounts = []

    @property
    def numAmounts(self):
        return len(self.amounts)

    @property
    def totalAmount(self):
        return sum(self.amounts)


class ChequeRow(object):

    def __init__(self):
        self.amounts = []


class Totals(object):

    def __init__(self, cashGroups, chequeColumns):
        self.numCheques = sum(c.numAmounts for c in chequeColumns)
        self.totalCheques = sum(c.totalAmount for c in chequeColumns)
        self.totalDeposit = sum(g.totalAmount for g in cashGroups) + \
                self.totalCheques

