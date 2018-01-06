"""
Configuration for Deacons application.
"""

import ceDataSource
import ceGUI
import ceODBC
import datetime
import os

class Config(ceGUI.Config):
    baseDsn = 'Driver=PostgreSQL;Servername=%s;Database=deacons;readonly=0'

    def ConnectToDataSource(self, app, appName):
        server = os.environ.get("DEACONS_DB_SERVER", "localhost")
        baseDsn = self.baseDsn % server
        dsn = "%s;uid=%s" % (baseDsn, os.environ["LOGNAME"])
        connection = ceODBC.Connection(dsn)
        return ceDataSource.ODBCDataSource(connection)

    def OnCreate(self):
        today = datetime.datetime.today()
        self.year = today.year

    def SelectYear(self):
        topWindow = ceGUI.AppTopWindow()
        with topWindow.OpenWindow("SelectDialogs.Year.Dialog") as dialog:
            if dialog.ShowModalOk():
                row = dialog.GetSelectedItem()
                self.year = row.year
                topWindow.OnYearChanged()

