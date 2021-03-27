"""
Calculate the budget requirement and collected amount year to date for the most
recent completed month. Also calculate the total amounts given to all causes
for the most recent completed month.
"""

import datetime
import decimal

from . import BaseReport

import Models

class Report(BaseReport):

    def _calc_max_date(self, cash_data, donations_data):
        max_cash_date = max(r.dateCollected for r in cash_data)
        max_donations_date = max(r.dateCollected for r in donations_data)
        max_date = max(max_cash_date, max_donations_date)
        num_days = (5 - max_date.weekday()) % 7 + 1
        next_sunday = max_date + datetime.timedelta(num_days)
        if next_sunday.month == max_date.month:
            start_of_month = datetime.date(max_date.year, max_date.month, 1)
            max_date = start_of_month - datetime.timedelta(1)
        return max_date

    def Run(self):
        year = Models.Years.GetRow(self.config.dataSource,
                                   year=self.config.year)
        cash_data = Models.CashSummary.GetRows(self.config.dataSource,
                                               year=self.config.year)
        donations_data = Models.DonationSummary.GetRows(self.config.dataSource,
                                                        year=self.config.year)
        max_date = self._calc_max_date(cash_data, donations_data)
        causes = Models.Causes.GetRows(self.config.dataSource,
                                       year=self.config.year)
        cause_dict = dict((c.causeId, c) for c in causes)
        data_by_cause = {}
        required_budget = CauseGroupData("Required Budget")
        required_budget.amount = (year.budgetAmount / 12) * max_date.month
        collected_budget = CauseGroupData("Collected Budget")
        for row in cash_data:
            if row.dateCollected > max_date:
                continue
            cause = cause_dict[row.causeId]
            if cause.description == "Budget":
                data = collected_budget
            else:
                data = data_by_cause.get(row.causeId)
                if data is None:
                    data = CauseGroupData(cause.description)
                    data_by_cause[row.causeId] = data
            data.amount += row.amount
        for row in donations_data:
            if row.dateCollected > max_date:
                continue
            cause = cause_dict[row.causeId]
            if cause.description == "Budget":
                data = collected_budget
            else:
                data = data_by_cause.get(row.causeId)
                if data is None:
                    data = CauseGroupData(cause.description)
                    data_by_cause[row.causeId] = data
            data.amount += row.chequeAmount
        cause_data = list(data_by_cause.values())
        cause_data.sort(key=lambda x: x.description.upper())
        self.config.GenerateXL("BulletinReport.xlml",
                               title=f'{max_date.strftime("%B %Y")} Report',
                               required_budget=required_budget,
                               collected_budget=collected_budget,
                               cause_data=cause_data)


class CauseGroupData:

    def __init__(self, description):
        self.description = description
        self.amount = 0.0
