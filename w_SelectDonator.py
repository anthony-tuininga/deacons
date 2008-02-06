"""
Dialog for selecting a donator.
"""

import ceDatabase
import ceGUI

class Dialog(ceGUI.SelectionListDialog):
    title = "Select Donator"


class List(ceGUI.List):
    singleSelection = True

    def OnCreate(self):
        self.AddColumn("lastName", "Last Name", 200)
        self.AddColumn("givenNames", "Given Names")


class DataSet(ceDatabase.DataSet):

    def _GetRows(self, cache, existingDonators = []):
        existingValues = dict.fromkeys(d.donatorId for d in existingDonators)
        return [d for d in cache.Donators() \
                if d.active and d.donatorId not in existingValues]

