'''
  agda-pkg
  ~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

# ----------------------------------------------------------------------------
from ..config import DATABASE_FILE_NAME, DATABASE_FILE_PATH
from ..config import DATABASE_SEARCH_INDEXES_PATH
from ..config import INDEX_REPOSITORY_PATH

from pony.orm   import *
from ponywhoosh import PonyWhoosh
import logging
import click_log as clog
# ----------------------------------------------------------------------------

# -- Logger def.
logger = logging.getLogger(__name__)
clog.basic_config(logger)

# -- Search index
pw = PonyWhoosh()

pw.indexes_path          = DATABASE_SEARCH_INDEXES_PATH
pw.search_string_min_len = 1
pw.writer_timeout        = 3

# -- Database
db = Database()

@pw.register_model('name', 'description', 'url')
class Library(db.Entity):
    name = PrimaryKey(str)
    localpath = Optional(str)
    description = Optional(str, nullable=True)
    url = Optional(str, nullable=True)
    versions = Set('LibraryVersion')
    appearson = Set('Dependency')
    keywords = Set('Keyword')
    installed = Optional(bool, default=False)
    default = Optional(bool, default=True)


@pw.register_model('name', 'sha', 'description', 'license')
class LibraryVersion(db.Entity):
    library = Required(Library)
    info_path = Optional(str, nullable=True, default=None)
    name = Optional(str, nullable=True, default=None)
    sha = Optional(str)
    valid = Optional(bool, default=False)
    description = Optional(str)
    license = Optional(str)
    testedWith = Set('TestedWith')
    keywords = Set('Keyword')
    requires = Set('Dependency')
    installed = Optional(bool, default=False)
    latest = Optional(bool, default=False)
    installation_path = Optional(str, default="")
    user_version = Optional(bool, default=False)

@pw.register_model('word')
class Keyword(db.Entity):
    word = PrimaryKey(str)
    libversions = Set(LibraryVersion)
    libraries = Set(Library)

@pw.register_model('agdaVersion')
class TestedWith(db.Entity):
    agdaVersion = PrimaryKey(str, auto=True)
    libraries = Set(LibraryVersion)

class Dependency(db.Entity):
    id = PrimaryKey(int, auto=True)
    library = Required(Library)
    minVersion = Optional(str, nullable=True)
    maxVersion = Optional(str, nullable=True)
    supporting = Set(LibraryVersion)

try:
  db.bind('sqlite', DATABASE_FILE_PATH.as_posix(), create_db=True)
  db.generate_mapping(create_tables=True)
except Exception as e:
  logger.error(e)
