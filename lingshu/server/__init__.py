"""LingShu server package boundary.

Framework behavior for this component is implemented by its assigned P1 issue.
"""

from lingshu.server.config import ServerConfig
from lingshu.server.server import Server, serve

__all__: tuple[str, ...] = (
    "Server",
    "ServerConfig",
    "serve",
)
