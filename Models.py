"""
Define models used by application.
"""

import ceGUI

class Causes(ceGUI.BaseModel):
    attrNames = "causeId description isReported isActive address"
    charBooleanAttrNames = "isReported isActive"
    extraAttrNames = "searchDescription"
    pkAttrNames = "causeId"
    cached = True


class Donators(ceGUI.BaseModel):
    attrNames = "donatorId isActive lastName givenNames address"
    charBooleanAttrNames = "isActive"
    extraAttrNames = "name reversedName searchName searchReversedName"
    pkAttrNames = "donatorId"
    cached = True


class DonatorsForYear(ceGUI.BaseModel):
    attrNames = "donatorId year assignedNumber"
    pkAttrNames = "year donatorId"
    cached = True

