"""
Main module for Deacons application.
"""

import ceGUI

class Deacons(ceGUI.Application):
    description = "Deacons"
    copyrightOwner = "Anthony Tuininga"
    copyrightStartYear = 1998
    copyrightEndYear = 2018
    configClassName = "Config.Config"


app = Deacons()
app.Run()

