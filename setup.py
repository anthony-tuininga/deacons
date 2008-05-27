import cx_Freeze
import glob
import os

executables = [cx_Freeze.Executable("Deacons.py")]

includes = [
        "Cache",
        "Common",
        "Database",
        "encodings.utf_8",
        "Reports",
        "r_ChequeLetter",
        "r_DepositCheques",
        "r_DepositSummary",
        "r_MonthlyReport",
        "r_QuarterlyReport",
        "r_TaxReceipts",
        "r_TreasurerSummary",
        "r_YearlyReport",
        "w_CashEdit",
        "w_CauseEdit",
        "w_Causes",
        "w_ChequeEdit",
        "w_CollectionEdit",
        "w_Deposits",
        "w_DonationsEdit",
        "w_Donators",
        "w_DonatorsForYear",
        "w_DonatorEdit",
        "w_DonatorForYearEdit",
        "w_ElderEdit",
        "w_Elders",
        "w_SelectCause",
        "w_SelectDate",
        "w_SelectDeposit",
        "w_SelectDonator",
        "w_SelectUnremitted",
        "w_SelectYear",
        "w_SplitDonationsEdit",
        "w_TaxReceipts",
        "w_TopLevelFrame",
        "w_YearEdit",
        "w_Years"
]

binIncludes = []
for name in glob.glob("/usr/lib/libwx*"):
    parts = os.path.basename(name).split(".")
    while parts[-1].isdigit():
        parts.pop(-1)
    binIncludes.append(".".join(parts))
includeFiles = [("CauseLetter.txt", "CauseLetter.txt")]

buildOptions = dict(
        compressed = True,
        includes = includes,
        bin_includes = binIncludes,
        include_files = includeFiles)

cx_Freeze.setup(
        name = "Deacons",
        version = "0.2",
        description = "Application for managing deacon data.",
        author = "Anthony Tuininga",
        author_email = "anthony.tuininga@gmail.com",
        executables = executables,
        options = dict(build_exe = buildOptions))

