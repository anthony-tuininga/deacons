import ceGUI
import ceODBC
import os

class Deacons(ceGUI.Application):
    description = "Deacons"
    copyrightOwner = "Anthony Tuininga"
    copyrightStartYear = copyrightEndYear = 2007
    version = "0.1"


class Config(object):
    baseDsn = 'Driver=PostgreSQL;Servername=localhost;Database=deacons'

    def __init__(self, app):
        dsn = "%s;uid=%s" % (self.baseDsn, os.environ["LOGNAME"])
        self.connection = ceODBC.Connection(dsn)

app = Deacons()
app.MainLoop()

