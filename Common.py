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

