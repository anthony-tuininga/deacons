"""
Panel which displays causes and enables editing of them.
"""

import ceDatabase
import ceGUI

from Cache import Cache

class Panel(ceGUI.DataListPanel):
    editDialogName = "w_CauseEdit.Dialog"
    updateSubCacheAttrName = "causes"

    def Retrieve(self):
        self.list.Retrieve(self.cache)


class List(ceGUI.DataList):

    def OnCreate(self):
        self.AddColumn("description", "Description")


class DataSet(ceDatabase.DataSet):
    rowClass = Cache.CausesSubCache.rowClass
    tableName = Cache.CausesSubCache.rowClass.tableName

    def _GetRows(self, cache):
        return cache.Causes()

