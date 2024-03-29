"""
Configuration for Deacons application.
"""

import ceDataSource
import ceGUI
import ceODBC
import datetime
import jinja2
import os
import srml2pdf
import subprocess
import tempfile
import xlml2xlsx

class Config(ceGUI.Config):
    baseDsn = 'Driver=PostgreSQL;Servername=%s;Database=deacons;readonly=0'

    def ConnectToDataSource(self, app, appName):
        server = os.environ.get("DEACONS_DB_SERVER", "localhost")
        baseDsn = self.baseDsn % server
        dsn = "%s;uid=%s" % (baseDsn, os.environ["LOGNAME"])
        connection = ceODBC.Connection(dsn)
        return ceDataSource.ODBCDataSource(connection)

    def GenerateXL(self, templateName, **args):
        template = self.templateEnv.get_template(templateName)
        renderedTemplate = template.render(**args)
        output = xlml2xlsx.GenerateXL(renderedTemplate)
        fileNo, outputFileName = tempfile.mkstemp(suffix = ".xlsx")
        os.write(fileNo, output.getvalue())
        os.close(fileNo)
        subprocess.Popen(["xdg-open", outputFileName])

    def GeneratePDF(self, templateName, **args):
        template = self.templateEnv.get_template(templateName)
        renderedTemplate = template.render(**args)
        output = srml2pdf.GeneratePDF(renderedTemplate)
        fileNo, outputFileName = tempfile.mkstemp(suffix = ".pdf")
        os.write(fileNo, output.getvalue())
        os.close(fileNo)
        subprocess.Popen(["xdg-open", outputFileName])

    def OnCreate(self):
        today = datetime.datetime.today()
        self.year = today.year
        self.templateEnv = jinja2.Environment(autoescape = True,
                loader = jinja2.FileSystemLoader(os.path.abspath("templates")))

    def RunReport(self, clsName):
        cls = ceGUI.GetModuleItem("ReportDefs.%s.Report" % clsName)
        report = cls(self)
        criteria = report.GetCriteria(ceGUI.AppTopWindow())
        if criteria is not None:
            report.Run(*criteria)

    def SelectYear(self):
        topWindow = ceGUI.AppTopWindow()
        with topWindow.OpenWindow("SelectDialogs.Year.Dialog") as dialog:
            if dialog.ShowModalOk():
                row = dialog.GetSelectedItem()
                self.year = row.year
                topWindow.OnYearChanged()

