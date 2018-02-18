"""
Define models used by application.
"""

import ceGUI

class Causes(ceGUI.BaseModel):
    attrNames = """causeId year description deductible reported
            donationAccountCode looseCashAccountCode notes"""
    charBooleanAttrNames = "deductible reported"
    extraAttrNames = "searchDescription"
    pkAttrNames = "causeId"
    cached = True


class Donations(ceGUI.BaseModel):
    tableName = "Donations_v"
    attrNames = """donationId dateDeposited dateCollected cash causeId
            donatorId amount"""
    charBooleanAttrNames = "cash"
    pkAttrNames = "donationId"


class Donators(ceGUI.BaseModel):
    attrNames = """donatorId year surname givenNames assignedNumber
            addressLine1 addressLine2 addressLine3"""
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
    extraAttrNames = "donator"
    pkAttrNames = "receiptNumber"


class Years(ceGUI.BaseModel):
    attrNames = "year budgetAmount receiptsIssued notes"
    charBooleanAttrNames = "receiptsIssued"
    pkAttrNames = "year"
    sortByAttrNames = "year"
    sortReversed = True
    cached = True

