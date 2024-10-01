from enum import Enum
from pathlib import Path

ENCODING = 'utf-8'

EXPECTED_STATUS = {
    'A': ('Active', 'Accepted'),
    'D': ('Deferred',),
    'F': ('Final',),
    'P': ('Provisional',),
    'R': ('Rejected',),
    'S': ('Superseded',),
    'W': ('Withdrawn',),
    '': ('Draft', 'Active'),
}

BASE_DIR = Path(__file__).parent

DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'

DATE_FORMAT = '%d.%m.%Y %H:%M:%S'

DL_LINK_PATTERN = r'.+pdf-a4\.zip$'

LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'

MAIN_DOC_URL = 'https://docs.python.org/3/'

MAIN_PEPS_URL = 'https://peps.python.org/'


class OutputTypeChoices(str, Enum):
    PRETTY = 'pretty'
    FILE = 'file'
