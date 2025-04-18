#!/usr/bin/env python3

# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Module defining the CharmState class which represents the state of the SMTP Integrator charm."""

import itertools
from dataclasses import dataclass
from typing import Optional

import ops
from charms.smtp_integrator.v0 import smtp
from pydantic import BaseModel, Field, ValidationError


class SmtpIntegratorConfig(BaseModel):
    """Represent charm builtin configuration values.

    Attributes:
        host: The hostname or IP address of the outgoing SMTP relay.
        port: The port of the outgoing SMTP relay.
        user: The SMTP AUTH user to use for the outgoing SMTP relay.
        password: The SMTP AUTH password to use for the outgoing SMTP relay.
        auth_type: The type used to authenticate with the SMTP relay.
        transport_security: The security protocol to use for the outgoing SMTP relay.
        domain: The domain used by the emails sent from SMTP relay.
        skip_ssl_verify: Specifies if certificate trust verification is skipped in the SMTP relay.
    """

    host: str = Field(..., min_length=1)
    port: int = Field(..., ge=1, le=65536)
    user: Optional[str] = None
    password: Optional[str] = None
    auth_type: smtp.AuthType | None = None
    transport_security: smtp.TransportSecurity | None = None
    domain: Optional[str] = None
    skip_ssl_verify: bool = False


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
        auth_type: The type used to authenticate with the SMTP relay.
        transport_security: The security protocol to use for the outgoing SMTP relay.
        domain: The domain used by the emails sent from SMTP relay.
        skip_ssl_verify: Specifies if certificate trust verification is skipped in the SMTP relay.
    """

    host: str
    port: int
    user: Optional[str]
    password: Optional[str]
    auth_type: Optional[smtp.AuthType]
    transport_security: Optional[smtp.TransportSecurity]
    domain: Optional[str]
    skip_ssl_verify: bool

    def __init__(self, *, smtp_integrator_config: SmtpIntegratorConfig):
        """Initialize a new instance of the CharmState class.

        Args:
            smtp_integrator_config: SMTP Integrator configuration.
        """
        self.host = smtp_integrator_config.host
        self.port = smtp_integrator_config.port
        self.user = smtp_integrator_config.user
        self.password = smtp_integrator_config.password
        self.auth_type = smtp_integrator_config.auth_type
        self.transport_security = smtp_integrator_config.transport_security
        self.domain = smtp_integrator_config.domain
        self.skip_ssl_verify = smtp_integrator_config.skip_ssl_verify

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
        try:
            # Incompatible with pydantic.AnyHttpUrl
            valid_config = SmtpIntegratorConfig(**dict(charm.config.items()))  # type: ignore
        except ValidationError as exc:
            error_fields = set(
                itertools.chain.from_iterable(error["loc"] for error in exc.errors())
            )
            error_field_str = " ".join(str(f) for f in error_fields)
            raise CharmConfigInvalidError(f"invalid configuration: {error_field_str}") from exc
        return cls(smtp_integrator_config=valid_config)
