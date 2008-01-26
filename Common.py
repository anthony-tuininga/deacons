"""
Commonly defined items.
"""

import ceGUI

class CauseColumn(ceGUI.ListColumn):

    def GetValue(self, row):
        causeId = getattr(row, self.attrName)
        if causeId is not None:
            cause = self.config.cache.CauseForId(causeId)
            return cause.description

    GetSortValue = GetValue


class AmountColumn(ceGUI.ListColumn):

    def GetValue(self, row):
        value = getattr(row, self.attrName)
        if value is None:
            return "$0.00"
        print "Transforming value", repr(value)
        if value < 1000:
            return "$%.2f" % value
        thousands = int(str(int(value))[:-3])
        number = "%.2f" % (value - 1000 * (thousands - 1))
        print "Thousands:", repr(thousands)
        print "Number:", repr(number)
        return "$%s,%s" % (str(thousands), number[1:])

