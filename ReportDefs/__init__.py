"""
Base class for all reports.
"""

class BaseReport(object):

    def __init__(self, config):
        self.config = config

    def GetCriteria(self, topWindow):
        return []

