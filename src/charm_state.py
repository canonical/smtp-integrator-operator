#!/usr/bin/env python3

# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

"""Module defining the CharmState class which represents the state of the SMTP Integrator charm."""

import itertools
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


class SmtpIntegratorConfig(BaseModel):  # pylint: disable=too-few-public-methods
    """Represent charm builtin configuration values.

    Attrs:
        host: The hostname or IP address of the outgoing SMTP relay.
        port: The port of the outgoing SMTP relay.
        user: The SMTP AUTH user to use for the outgoing SMTP relay.
        password: The SMTP AUTH password to use for the outgoing SMTP relay.
        auth_type: The type used to authenticate with the SMTP relay.
        transport_security: The security protocol to use for the outgoing SMTP relay.
        domain: The domain used by the sent emails from SMTP relay.
    """

    host: str = Field(..., min_length=1)
    port: int
    user: Optional[str]
    password: Optional[str]
    auth_type: Optional[smtp.AuthType]
    transport_security: Optional[smtp.TransportSecurity]
    domain: Optional[str]


class CharmConfigInvalidError(Exception):
    """Exception raised when a charm configuration is found to be invalid.

    Attrs:
        msg (str): Explanation of the error.
    """

    def __init__(self, msg: str):
        """Initialize a new instance of the CharmConfigInvalidError exception.

        Args:
            msg (str): Explanation of the error.
        """
        self.msg = msg


class CharmState:
    """Represents the state of the SMTP Integrator charm.

    Attrs:
        host: The hostname or IP address of the outgoing SMTP relay.
        port: The port of the outgoing SMTP relay.
        user: The SMTP AUTH user to use for the outgoing SMTP relay.
        password: The SMTP AUTH password to use for the outgoing SMTP relay.
        auth_type: The type used to authenticate with the SMTP relay.
        transport_security: The security protocol to use for the outgoing SMTP relay.
        domain: The domain used by the sent emails from SMTP relay.
    """

    def __init__(self, *, smtp_integrator_config: SmtpIntegratorConfig):
        """Initialize a new instance of the CharmState class.

        Args:
            smtp_integrator_config: SMTP Integrator configuration.
        """
        self._smtp_integrator_config = smtp_integrator_config

    @property
    def host(self) -> str:
        """Return host config.

        Returns:
            str: host config.
        """
        return self._smtp_integrator_config.host

    @property
    def port(self) -> int:
        """Return port config.

        Returns:
            int: port config.
        """
        return self._smtp_integrator_config.port

    @property
    def user(self) -> Optional[str]:
        """Return user config.

        Returns:
            str: user config.
        """
        return self._smtp_integrator_config.user

    @property
    def password(self) -> Optional[str]:
        """Return password config.

        Returns:
            str: password config.
        """
        return self._smtp_integrator_config.password

    @property
    def auth_type(self) -> smtp.AuthType:
        """Return auth_type config.

        Returns:
            AuthType: auth_type config.
        """
        return self._smtp_integrator_config.auth_type

    @property
    def transport_security(self) -> smtp.TransportSecurity:
        """Return transport_security config.

        Returns:
            TransportSecurity: transport_security config.
        """
        return self._smtp_integrator_config.transport_security

    @property
    def domain(self) -> Optional[str]:
        """Return domain config.

        Returns:
            str: domain config.
        """
        return self._smtp_integrator_config.domain

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
