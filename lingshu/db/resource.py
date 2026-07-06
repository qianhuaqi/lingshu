"""Database resource lifecycle boundary."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from lingshu.core.errors import SafeDetails, freeze_safe_details

from .config import DatabaseConfig
from .driver import DatabaseDriver
from .errors import DatabaseConfigurationError, DatabaseError, DatabaseLifecycleError

_UNSET = object()


class _DatabaseResourceState(StrEnum):
    REGISTERED = "registered"
    STARTED = "started"
    STOPPED = "stopped"


@dataclass(slots=True)
class DatabaseResource:
    """Named database resource whose network work is limited to startup/shutdown."""

    config: DatabaseConfig
    driver: DatabaseDriver
    _state: _DatabaseResourceState = field(
        init=False,
        default=_DatabaseResourceState.REGISTERED,
        repr=False,
    )
    _handle: object = field(init=False, default=_UNSET, repr=False)

    def __post_init__(self) -> None:
        if self.driver.backend != self.config.backend:
            raise DatabaseConfigurationError(
                "db.configuration.backend_mismatch",
                "Database driver backend must match the resource configuration.",
                safe_details=self.config.safe_details,
            )

    @property
    def name(self) -> str:
        return self.config.name

    @property
    def backend(self) -> str:
        return self.config.backend

    @property
    def started(self) -> bool:
        return self._state is _DatabaseResourceState.STARTED

    @property
    def safe_details(self) -> SafeDetails:
        details = dict(self.config.safe_details)
        details["state"] = self._state.value
        return freeze_safe_details(details)

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(name={self.name!r}, backend={self.backend!r}, "
            f"state={self._state.value!r})"
        )

    async def startup(self) -> None:
        if self._state is not _DatabaseResourceState.REGISTERED:
            raise DatabaseLifecycleError(
                "db.lifecycle.invalid_startup_state",
                "Database resources can start only from the registered state.",
                safe_details=self.safe_details,
            )
        try:
            self._handle = await self.driver.startup(self.config)
        except DatabaseError:
            raise
        except Exception as exc:
            raise DatabaseLifecycleError(
                "db.lifecycle.startup_failed",
                "Database resource startup failed.",
                safe_details=self.safe_details,
                cause=exc,
            ) from exc
        self._state = _DatabaseResourceState.STARTED

    async def shutdown(self) -> None:
        if self._state is _DatabaseResourceState.REGISTERED:
            self._state = _DatabaseResourceState.STOPPED
            return
        if self._state is _DatabaseResourceState.STOPPED:
            return

        try:
            await self.driver.shutdown(self._handle)
        except DatabaseError:
            raise
        except Exception as exc:
            raise DatabaseLifecycleError(
                "db.lifecycle.shutdown_failed",
                "Database resource shutdown failed.",
                safe_details=self.safe_details,
                cause=exc,
            ) from exc
        finally:
            self._handle = _UNSET
            self._state = _DatabaseResourceState.STOPPED


__all__ = ("DatabaseResource",)
