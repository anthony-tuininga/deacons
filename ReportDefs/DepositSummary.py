"""
Print a report of the cheques, coin and cash deposited for a particular date.
"""

from . import BaseReport

import Models

class Report(BaseReport):

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
        chequeColumns = [ChequeColumn() for i in range(8)]
        cheques = Models.DepositCheques.GetRows(self.config.dataSource,
                dateDeposited = dateDeposited)
        rawChequesPerColumn = len(cheques) / len(chequeColumns)
        chequesPerColumn = int(rawChequesPerColumn)
        if chequesPerColumn < rawChequesPerColumn:
            chequesPerColumn += 1
        for column in chequeColumns:
            column.amounts.extend(c.amount for c in cheques[:chequesPerColumn])
            cheques = cheques[chequesPerColumn:]
        chequeRows = []
        for ix in range(chequesPerColumn):
            row = ChequeRow()
            chequeRows.append(row)
            for column in chequeColumns:
                if ix < len(column.amounts):
                    row.amounts.append(column.amounts[ix])
        totalRow = ChequeRow()
        for column in chequeColumns:
            totalRow.amounts.append(sum(column.amounts))
        chequeRows.append(totalRow)
        self.config.GeneratePDF("DepositSummary.rml",
                cashGroups = [coinGroup, cashGroup], chequeRows = chequeRows,
                dateDeposited = dateDeposited)


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

    def __init__(self):
        self.amounts = []


class ChequeRow(object):

    def __init__(self):
        self.amounts = []

