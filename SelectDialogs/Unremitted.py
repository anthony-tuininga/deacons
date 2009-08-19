"""
Dialog for selecting an unremitted amount for a cheque.
"""

import ceDatabase
import ceGUI
import wx

import Common

class Dialog(ceGUI.SelectionListDialog):
    title = "Select unremitted amount"
    defaultSize = (355, 310)


class List(ceGUI.List):
    singleSelection = True

    def OnCreate(self):
        self.AddColumn("causeId", "Cause", 225, cls = Common.CauseColumn)
        self.AddColumn("amount", "Amount", cls = Common.AmountColumn,
                justification = wx.LIST_FORMAT_RIGHT)


class DataSet(ceDatabase.DataSet):
    attrNames = "causeId amount"

    def _GetSqlForRetrieve(self):
        return """
                select
                  ua.CauseId,
                  sum(ca.ChequeAmount + ca.CashAmount)
                from
                  UnremittedAmounts ua
                  join CollectionAmounts ca
                      on ca.CollectionId = ua.CollectionId
                      and ca.CauseId = ua.CauseId
                where ua.CauseId in
                    ( select ua.CauseId
                      from
                        UnremittedAmounts ua
                        join Collections c
                            on c.CollectionId = ua.CollectionId
                      where c.DepositId = ?
                    )
                group by ua.CauseId"""

