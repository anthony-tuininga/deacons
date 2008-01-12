import cx_Freeze

executables = [cx_Freeze.Executable("Deacons.py")]

includes = [
        "Database",
        "encodings.utf_8",
        "w_Elders",
        "w_TopLevelFrame"
]

buildOptions = dict(
        compressed = True,
        includes = includes)

cx_Freeze.setup(
        name = "Deacons",
        version = "0.1",
        description = "Application for managing deacon data.",
        author = "Anthony Tuininga",
        author_email = "anthony.tuininga@gmail.com",
        executables = executables,
        options = dict(build_exe = buildOptions))

