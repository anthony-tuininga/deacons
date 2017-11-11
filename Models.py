"""
Define models used by application.
"""

import ceGUI

class Causes(ceGUI.BaseModel):
    attrNames = "causeId year description deductible reported notes"
    charBooleanAttrNames = "deductible reported"
    extraAttrNames = "searchDescription"
    pkAttrNames = "causeId"
    cached = True


class Donators(ceGUI.BaseModel):
    attrNames = "donatorId year surname givenNames assignedNumber address"
    extraAttrNames = "name searchName"
    pkAttrNames = "donatorId"
    cached = True

    @classmethod
    def SetExtraAttributes(cls, dataSource, rows):
        for row in rows:
            row.name = row.surname if row.givenNames is None \
                    else "%s, %s" % (row.surname, row.givenNames)
            row.searchName = row.name.upper()


class TaxReceipts(ceGUI.BaseModel):
    attrNames = """receiptNumber year donatorId amount dateIssued isDuplicate
            canceled"""
    charBooleanAttrNames = "isDuplicate canceled"
    pkAttrNames = "receiptNumber"


class Years(ceGUI.BaseModel):
    attrNames = "year budgetAmount promptForReceiptGeneration receiptsIssued"
    charBooleanAttrNames = "promptForReceiptGeneration receiptsIssued"
    pkAttrNames = "year"
    cached = True

