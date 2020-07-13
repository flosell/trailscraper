"""Module for LocalDirectoryRecordSource"""
import logging
import os

from toolz import pipe
from toolz.curried import filter as filterz
from toolz.curried import last as lastz
from toolz.curried import map as mapz
from toolz.curried import mapcat as mapcatz
from toolz.curried import sorted as sortedz

from trailscraper.cloudtrail import LogFile


class LocalDirectoryRecordSource():
    """Class to represent cloudtrail records stored on disk"""
    def __init__(self, log_dir):
        self._log_dir = log_dir

    def _valid_log_files(self):
        def _valid_or_warn(log_file):
            if log_file.has_valid_filename():
                return True

            logging.warning("Invalid filename: %s", log_file.filename())
            return False

        def _to_paths(triple):
            root, _, files_in_dir = triple
            return [os.path.join(root, file_in_dir) for file_in_dir in files_in_dir]

        return pipe(os.walk(self._log_dir),
                    mapcatz(_to_paths),
                    mapz(LogFile),
                    filterz(_valid_or_warn))

    def load_from_dir(self, from_date, to_date):
        """Loads all CloudTrail Records in a file"""
        records = []
        for logfile in self._valid_log_files():
            if logfile.contains_events_for_timeframe(from_date, to_date):
                records.extend(logfile.records())

        return records

    def last_event_timestamp_in_dir(self):
        """Return the timestamp of the most recent event in the given directory"""
        most_recent_file = pipe(self._valid_log_files(),
                                sortedz(key=LogFile.timestamp),
                                lastz,
                                LogFile.records,
                                sortedz(key=lambda record: record.event_time),
                                lastz)

        return most_recent_file.event_time
