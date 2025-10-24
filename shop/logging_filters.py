import logging


class IgnoreStaticFilesFilter(logging.Filter):
    def filter(self, record):
        # Return False if the message contains '/static/',
        # to exclude these entries from the logs.
        message = record.getMessage()
        return '/static/' not in message