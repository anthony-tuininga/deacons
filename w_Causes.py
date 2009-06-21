"""
Panel which displays causes and enables editing of them.
"""

import ceDatabase
import ceGUI

from Cache import Cache

class Panel(ceGUI.DataListPanel):
    editDialogName = "w_CauseEdit.Dialog"
    updateSubCacheAttrName = "causes"


class List(ceGUI.DataList):

    def OnCreate(self):
        self.AddColumn("description", "Description")

    def Retrieve(self):
        super(List, self).Retrieve(self.cache)


class DataSet(ceDatabase.DataSet):
    rowClass = Cache.CausesSubCache.rowClass
    tableName = Cache.CausesSubCache.rowClass.tableName

    def _GetRows(self, cache):
        return cache.Causes()

