import ceDatabase
import ceGUI
import cx_Exceptions
import wx

class Panel(ceGUI.Panel):

    def OnCreate(self):
        self.depositedDateLabel = self.AddLabel()
        self.notebook = ceGUI.Notebook(self)
        page = CollectionsPanel(self.notebook)
        page.RestoreSettings()
        self.notebook.AddPage(page, "Collections")

    def OnLayout(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.depositedDateLabel, flag = wx.ALL, border = 5)
        sizer.Add(self.notebook, flag = wx.EXPAND, proportion = 1)
        return sizer

    def Retrieve(self, depositId, dateDeposited):
        label = "Deposited %s" % dateDeposited.strftime("%A, %B %d, %Y")
        self.depositedDateLabel.SetLabel(label)
        for page in self.notebook.IterPages():
            page.Retrieve()


class CollectionsPanel(ceGUI.DataListPanel):
    listClassName = "CollectionsList"


class CollectionsList(ceGUI.DataList):
    dataSetClassName = "CollectionsDataSet"

    def OnCreate(self):
        self.AddColumn("dateCollected", "Date")
        self.AddColumn("description", "Description")


class CollectionsDataSet(ceDatabase.DataSet):
    tableName = "Collections"
    attrNames = "collectionId causeId dateCollected reconciled description"
    retrievalAttrNames = "depositId"
    pkAttrNames = "collectionId"

