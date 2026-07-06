"""Import-safe database foundation contracts.

Importing ``lingshu.db`` defines contracts only. It does not import database
client libraries, open sockets, connect to services, or mutate application state.
"""

from lingshu.db.config import DatabaseConfig
from lingshu.db.driver import DatabaseDriver
from lingshu.db.errors import (
    DatabaseConfigurationError,
    DatabaseError,
    DatabaseLifecycleError,
)
from lingshu.db.manager import DatabaseManager
from lingshu.db.resource import DatabaseResource

__all__ = (
    "DatabaseConfig",
    "DatabaseConfigurationError",
    "DatabaseDriver",
    "DatabaseError",
    "DatabaseLifecycleError",
    "DatabaseManager",
    "DatabaseResource",
)
