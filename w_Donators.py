"""
Panel which displays donators and enables editing of them.
"""

import ceDatabase
import ceGUI

from Cache import Cache

class Panel(ceGUI.DataListPanel):
    editDialogName = "w_DonatorEdit.Dialog"
    updateSubCacheAttrName = "donators"

    def Retrieve(self):
        self.list.Retrieve(self.cache)


class List(ceGUI.DataList):

    def OnCreate(self):
        self.AddColumn("lastName", "Last Name", 200)
        self.AddColumn("givenNames", "Given Names")


class DataSet(ceDatabase.DataSet):
    rowClass = Cache.DonatorsSubCache.rowClass
    tableName = Cache.DonatorsSubCache.rowClass.tableName

    def _GetRows(self, cache):
        return cache.Donators()

