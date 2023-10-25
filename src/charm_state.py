#!/usr/bin/env python3

# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

"""Module defining the CharmState class which represents the state of the SMTP Integrator charm."""

import itertools
from dataclasses import dataclass
from typing import Optional

import ops
from charms.smtp_integrator.v0 import smtp
from pydantic import BaseModel, Field, ValidationError

KNOWN_CHARM_CONFIG = (
    "host",
    "port",
    "user",
    "password",
    "auth_type",
    "transport_security",
    "domain",
)


class SmtpIntegratorConfig(BaseModel):
    """Represent charm builtin configuration values.

    Attributes:
        host: The hostname or IP address of the outgoing SMTP relay.
        port: The port of the outgoing SMTP relay.
        user: The SMTP AUTH user to use for the outgoing SMTP relay.
        password: The SMTP AUTH password to use for the outgoing SMTP relay.
        auth_type: The type used to authenticate with the SMTP relay.
        transport_security: The security protocol to use for the outgoing SMTP relay.
        domain: The domain used by the sent emails from SMTP relay.
    """

    host: str = Field(..., min_length=1)
    port: int = Field(None, ge=1, le=65536)
    user: Optional[str]
    password: Optional[str]
    auth_type: Optional[smtp.AuthType]
    transport_security: Optional[smtp.TransportSecurity]
    domain: Optional[str]


class CharmConfigInvalidError(Exception):
    """Exception raised when a charm configuration is found to be invalid.

    Attributes:
        msg (str): Explanation of the error.
    """

    def __init__(self, msg: str):
        """Initialize a new instance of the CharmConfigInvalidError exception.

        Args:
            msg (str): Explanation of the error.
        """
        self.msg = msg


@dataclass
class CharmState:  # pylint: disable=too-many-instance-attributes
    """Represents the state of the SMTP Integrator charm.

    Attributes:
        host: The hostname or IP address of the outgoing SMTP relay.
        port: The port of the outgoing SMTP relay.
        user: The SMTP AUTH user to use for the outgoing SMTP relay.
        password: The SMTP AUTH password to use for the outgoing SMTP relay.
        password_id: The secret ID where the SMTP AUTH password for the SMTP relay is stored.
        auth_type: The type used to authenticate with the SMTP relay.
        transport_security: The security protocol to use for the outgoing SMTP relay.
        domain: The domain used by the sent emails from SMTP relay.
    """

    host: str
    port: int
    user: Optional[str]
    password: Optional[str]
    password_id: Optional[str]
    auth_type: Optional[smtp.AuthType]
    transport_security: Optional[smtp.TransportSecurity]
    domain: Optional[str]

    def __init__(self, *, smtp_integrator_config: SmtpIntegratorConfig):
        """Initialize a new instance of the CharmState class.

        Args:
            smtp_integrator_config: SMTP Integrator configuration.
        """
        self.host = smtp_integrator_config.host
        self.port = smtp_integrator_config.port
        self.user = smtp_integrator_config.user
        self.password = smtp_integrator_config.password
        self.password_id = None
        self.auth_type = smtp_integrator_config.auth_type
        self.transport_security = smtp_integrator_config.transport_security
        self.domain = smtp_integrator_config.domain

    @classmethod
    def from_charm(cls, charm: "ops.CharmBase") -> "CharmState":
        """Initialize a new instance of the CharmState class from the associated charm.

        Args:
            charm: The charm instance associated with this state.

        Return:
            The CharmState instance created by the provided charm.

        Raises:
            CharmConfigInvalidError: if the charm configuration is invalid.
        """
        config = {k: v for k, v in charm.config.items() if k in KNOWN_CHARM_CONFIG}
        try:
            # Incompatible with pydantic.AnyHttpUrl
            valid_config = SmtpIntegratorConfig(**config)  # type: ignore
        except ValidationError as exc:
            error_fields = set(
                itertools.chain.from_iterable(error["loc"] for error in exc.errors())
            )
            error_field_str = " ".join(str(f) for f in error_fields)
            raise CharmConfigInvalidError(f"invalid configuration: {error_field_str}") from exc
        return cls(smtp_integrator_config=valid_config)
