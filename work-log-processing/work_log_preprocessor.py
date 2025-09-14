"""Module for preprocessing personal work log."""

from datetime import date, datetime
import re
import sys
import uuid

ACTIVITY_PREFIX = '- '
DELIMITER = ' - '
ENCODING = 'utf-8'
LOG_DATE_FORMAT = '%Y.%m.%d'
LOG_ENTRY_START_PATTERN = r'^\d{4}.\d{2}.\d{2}.*$'
LOG_TIME_FORMAT = '%H:%M'

class LogEntry:
    """An entry in the work log corresponding to a particular datetime pair."""

    activities: list[str]
    """Activities done between the clock-in and clock-out datetimes."""
    clock_in: date | None
    """Clock-in datetime represented in `YYYY-MM-DD HH:MM:SS` format."""
    clock_out: date | None
    """Clock-out datetime represented in `YYYY-MM-DD HH:MM:SS` format."""
    key: str
    """Unique key to identify the log entry."""
    log_date: date | None
    """Log entry date represented in `YYYY-MM-DD` format."""
    log_type: str
    """Whether the log entry is a holiday, an offset, an onsite, or a work-from-home entry."""

    def __generate_key(self):
        """Generate a key based from the clock-in and clock-out datetimes."""

        if self.clock_in is None or self.clock_out is None:
            return str(uuid.uuid4())

        return re.sub(
            r'\D', 
            '',
            f'{self.clock_in}{self.clock_out}'
        )

    def __get_date(self, log_date: str):
        """Transform a log date string as a date if possible; return `None` otherwise."""

        try:
            return datetime \
                .strptime(log_date, LOG_DATE_FORMAT) \
                .date()
        except (OverflowError, NotImplementedError, TypeError, ValueError):
            return None

    def __get_datetime(self, log_time: str):
        """Transform a log datetime string as a datetime if possible; return `None` otherwise."""

        try:
            if self.log_date is None:
                raise TypeError

            return datetime.combine(
                self.log_date,
                datetime \
                    .strptime(log_time, LOG_TIME_FORMAT) \
                    .time()
            )
        except (OverflowError, NotImplementedError, TypeError, ValueError):
            return None

    def __init__(self, line: str):
        """Initialize a log entry from a log file line."""

        [
            log_date,
            clock_in,
            clock_out,
            log_type,
        ] = line \
            .strip() \
            .split(DELIMITER)

        self.activities = []
        self.log_type = log_type

        """@README

        Preserve the initialization order below as some methods require
        some properties to have been initialized beforehand.
        """
        self.log_date = self.__get_date(log_date)

        self.clock_in = self.__get_datetime(clock_in)
        self.clock_out = self.__get_datetime(clock_out)

        self.key = self.__generate_key()

    def __repr__(self):
        """Represent the log entry as a JSON object on print."""

        return (
          '{\n'
          f'  activities: {self.activities}\n'
          f'  clock-in: {self.clock_in}\n'
          f'  clock-out: {self.clock_out}\n'
          f'  key: {self.key}\n'
          f'  log-date: {self.log_date}\n'
          f'  log-type: {self.log_type}\n'
          '}'
        )

def preprocess_work_log(filepath: str) -> None:
    """Parse work log in specified file path then print each entry in console as JSON objects."""

    log_file = open(filepath, encoding=ENCODING)

    current_key: str = ''
    entries: dict[str, LogEntry] = {}

    for log_line in log_file:
        if re.match(LOG_ENTRY_START_PATTERN, log_line):
            entry = LogEntry(log_line)

            current_key = entry.key

            entries[entry.key] = entry
        elif log_line.startswith(ACTIVITY_PREFIX):
            entries \
                [current_key] \
                .activities \
                .append(
                    log_line \
                        .strip() \
                        .removeprefix(ACTIVITY_PREFIX)
                )

    for entry in entries.values():
        print(entry)

    log_file.close()

preprocess_work_log(sys.argv[1])
