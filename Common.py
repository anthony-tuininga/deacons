"""
Commonly defined items.
"""

import ceGUI
import decimal
import wx

def FormattedAmount(value):
    if value is None:
        return "$0.00"
    if value < 1000:
        return "$%.2f" % value
    thousands = int(str(int(value))[:-3])
    number = "%.2f" % (value - 1000 * (thousands - 1))
    return "$%s,%s" % (str(thousands), number[1:])


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
        return FormattedAmount(value)


class AmountField(ceGUI.TextField):

    def _Initialize(self):
        super(AmountField, self)._Initialize()
        ceGUI.EventHandler(self.GetParent(), self, wx.EVT_CHAR, self.OnChar,
                skipEvent = False)
                
    def GetValue(self):
        value = super(AmountField, self).GetValue()
        if value is not None:
            return decimal.Decimal(value.replace("$", "").replace(",", ""))
            
    def OnChar(self, event):
        key = event.GetKeyCode()
        if key in (wx.WXK_BACK, wx.WXK_DELETE) or key > 127:
            event.Skip()
        if key >= ord('0') and key <= ord('9'):
            event.Skip()
        if key == ord('$') or key == ord(','):
            event.Skip()
            
    def SetValue(self, value):
        if value is not None:
            value = FormattedAmount(value)
        super(AmountField, self).SetValue(value)


class Panel(ceGUI.Panel):

    def PrintReport(self, name):
        cls = ceGUI.GetModuleItem(name, "Report")
        report = cls(self)
        report.Print()

