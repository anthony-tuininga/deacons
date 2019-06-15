"""
Calculate the donations and loose cash for each cause for each collection and
generate a PDF for distribution to the treasurer.
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
        rawCash = Models.CashSummary.GetRows(self.config.dataSource,
                dateDeposited = dateDeposited)
        rawDonations = Models.DonationSummary.GetRows(self.config.dataSource,
                dateDeposited = dateDeposited)
        causeDict = dict((c.causeId, c.description) for c in \
                Models.Causes.GetRows(self.config.dataSource,
                        year = self.config.year))
        collectionDict = {}
        for row in rawDonations:
            collection = collectionDict.get(row.dateCollected)
            if collection is None:
                collection = Collection(row.dateCollected)
                collectionDict[row.dateCollected] = collection
            cause = collection.GetRowForCause(row.causeId,
                    causeDict[row.causeId])
            cause.chequeAmount += row.chequeAmount
            cause.envelopeCash += row.cashAmount
        for row in rawCash:
            collection = collectionDict.get(row.dateCollected)
            if collection is None:
                collection = Collection(row.dateCollected)
                collectionDict[row.dateCollected] = collection
            cause = collection.GetRowForCause(row.causeId,
                    causeDict[row.causeId])
            cause.cashAmount += row.amount
        collections = [collectionDict[i] for i in sorted(collectionDict)]
        for collection in collections:
            collection.PrepareForReport()
        collections[-1].finalCollection = True
        self.config.GeneratePDF("TreasurerSummaryByCollection.rml",
                collections = collections)


class Collection(object):

    def __init__(self, dateCollected):
        self.dateCollected = dateCollected
        self.causes = []
        self.causeDict = {}
        self.finalCollection = False

    def GetRowForCause(self, causeId=None, causeDescription=""):
        row = self.causeDict.get(causeId)
        if row is None:
            row = self.causeDict[causeId] = Cause(causeDescription)
            self.causes.append(row)
        return row

    def PrepareForReport(self):
        self.causes = list(self.causeDict.values())
        self.causes.sort(key = lambda x: x.description)
        totals = Cause()
        for cause in self.causes:
            totals.chequeAmount += cause.chequeAmount
            totals.envelopeCash += cause.envelopeCash
            totals.cashAmount += cause.cashAmount
        self.causes.append(totals)


class Cause(object):

    def __init__(self, description=""):
        self.description = description
        self.chequeAmount = 0
        self.envelopeCash = 0
        self.cashAmount = 0

    @property
    def looseCash(self):
        return self.cashAmount - self.envelopeCash

    @property
    def totalAmount(self):
        return self.chequeAmount + self.cashAmount
