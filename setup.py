import cx_Freeze
import glob
import os

executables = [cx_Freeze.Executable("Deacons.py")]

includes = [
        "Cache",
        "Common",
        "Config",
        "w_Causes",
        "w_CausesForYear",
        "w_Deposits",
        "w_Donators",
        "w_DonatorsForYear",
        "w_Elders",
        "w_TaxReceipts",
        "w_TopLevelFrame",
        "w_Years"
]

packages = [
        "EditDialogs",
        "ReportDefs",
        "SelectDialogs"
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
        packages = packages,
        bin_includes = binIncludes,
        include_files = includeFiles)

cx_Freeze.setup(
        name = "Deacons",
        version = "3.1",
        description = "Application for managing deacon data.",
        author = "Anthony Tuininga",
        author_email = "anthony.tuininga@gmail.com",
        executables = executables,
        options = dict(build_exe = buildOptions))

