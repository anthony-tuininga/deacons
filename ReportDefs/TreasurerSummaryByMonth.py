"""
Calculate the donations and loose cash for each cause for each month and
generate an Excel document for distribution to the treasurer.
"""

import datetime

from . import BaseReport

import Models

class Report(BaseReport):

    def Run(self):
        rawCash = Models.CashSummary.GetRows(self.config.dataSource,
                year = self.config.year)
        maxCashMonth = max(r.dateCollected.month for r in rawCash)
        rawDonations = Models.DonationSummary.GetRows(self.config.dataSource,
                year = self.config.year)
        maxDonationMonth = max(r.dateCollected.month for r in rawDonations)
        numMonths = max(maxCashMonth, maxDonationMonth)
        months = [datetime.date(self.config.year, m + 1, 1) \
                for m in range(numMonths)]
        rawCauses = Models.Causes.GetRows(self.config.dataSource,
                year = self.config.year)
        rawCauses.sort(key = lambda x: x.description.upper())
        causeGroups = [CauseGroupData(months, True),
                CauseGroupData(months, False)]
        causeDict = {}
        for rawCause in rawCauses:
            cause = CauseData(rawCause, months)
            ix = int(not rawCause.deductible)
            causeGroups[ix].causes.append(cause)
            causeDict[rawCause.causeId] = cause
        causeGroups[1].prevRowIndex = 0 - len(causeGroups[1].causes) - 6
        for row in rawCash:
            cause = causeDict[row.causeId]
            month = cause.months[row.dateCollected.month - 1]
            month.looseCash += row.amount
        for row in rawDonations:
            cause = causeDict[row.causeId]
            month = cause.months[row.dateCollected.month - 1]
            month.looseCash -= row.cashAmount
            month.donations += row.chequeAmount + row.cashAmount
        formulaParts = ["RC[%d]" % ((i + 1) * -3) for i in range(numMonths)]
        grandTotalFormula = "+".join(formulaParts)
        self.config.GenerateXL("TreasurerSummaryByMonth.xlml",
                overallTitleMergeAcross = 3 * (numMonths + 1), months = months,
                causeGroups = causeGroups,
                grandTotalFormula = grandTotalFormula)


class CauseGroupData(object):

    def __init__(self, months, deductible):
        self.months = months
        self.causes = []
        self.description = "Deductible Causes"
        if not deductible:
            self.description = "Not " + self.description


class CauseData(object):

    def __init__(self, cause, months):
        self.description = cause.description
        self.months = [MonthData(m) for m in months]


class MonthData(object):

    def __init__(self, sampleDate):
        self.sampleDate = sampleDate
        self.donations = 0
        self.looseCash = 0

