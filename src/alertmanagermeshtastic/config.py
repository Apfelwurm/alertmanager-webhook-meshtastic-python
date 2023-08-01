"""
alertmanagermeshtastic.config
~~~~~~~~~~~~~~~~~~

Configuration loading

:Copyright: 2007-2022 Jochen Kupperschmidt, Alexander Volz
:License: MIT, see LICENSE for details.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import rtoml

DEFAULT_HTTP_HOST = '127.0.0.1'
DEFAULT_HTTP_PORT = 9119
DEFAULT_MESHTASTIC_NODEID = 123456789
DEFAULT_MESHTASTIC_MAXSENDINGATTEMPTS = 5
DEFAULT_MESHTASTIC_TIMEOUT = 60


class ConfigurationError(Exception):
    """Indicates a configuration error."""


@dataclass(frozen=True)
class Config:
    log_level: str
    http: HttpConfig
    meshtastic: MeshtasticConfig


@dataclass(frozen=True)
class HttpConfig:
    """An HTTP receiver configuration."""

    host: str
    port: int


@dataclass(frozen=True)
class MeshtasticConnection:
    """An MESHTASTIC connection."""

    tty: str
    nodeid: int = DEFAULT_MESHTASTIC_NODEID
    maxsendingattempts: int = DEFAULT_MESHTASTIC_MAXSENDINGATTEMPTS
    timeout: int = DEFAULT_MESHTASTIC_TIMEOUT


@dataclass(frozen=True)
class MeshtasticConfig:
    """An MESHTASTIC Interface configuration."""

    connection: Optional[MeshtasticConnection]


def load_config(path: Path) -> Config:
    """Load configuration from file."""
    data = rtoml.load(path)

    log_level = _get_log_level(data)
    http_config = _get_http_config(data)
    meshtastic_config = _get_meshtastic_config(data)

    return Config(
        log_level=log_level,
        http=http_config,
        meshtastic=meshtastic_config,
    )


def _get_log_level(data: dict[str, Any]) -> str:
    level = data.get('log_level', 'debug').upper()

    if level not in {'CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'}:
        raise ConfigurationError(f'Unknown log level "{level}"')

    return level


def _get_http_config(data: dict[str, Any]) -> HttpConfig:
    data_http = data.get('http', {})

    host = data_http.get('host', DEFAULT_HTTP_HOST)
    port = int(data_http.get('port', DEFAULT_HTTP_PORT))

    return HttpConfig(host, port)


def _get_meshtastic_config(data: dict[str, Any]) -> MeshtasticConfig:
    data_meshtastic = data['meshtastic']

    connection = _get_meshtastic_connection(data_meshtastic)

    return MeshtasticConfig(
        connection=connection,
    )


def _get_meshtastic_connection(
    data_meshtastic: Any,
) -> Optional[MeshtasticConnection]:
    data_connection = data_meshtastic.get('connection')
    if data_connection is None:
        return None

    maxsendingattempts = data_connection.get('maxsendingattempts')
    timeout = data_connection.get('timeout')
    tty = data_connection.get('tty')
    if not tty:
        return None

    nodeid = int(data_connection.get('nodeid', DEFAULT_MESHTASTIC_NODEID))

    return MeshtasticConnection(
        tty=tty,
        nodeid=nodeid,
        maxsendingattempts=maxsendingattempts,
        timeout=timeout,
    )
