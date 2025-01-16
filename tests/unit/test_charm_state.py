# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""CharmState unit tests."""

from unittest.mock import MagicMock

import pytest

from charm_state import CharmConfigInvalidError, CharmState


def test_charm_state_from_charm():
    """
    arrange: set up a configured charm
    act: access the status properties
    assert: the configuration is accessible from the state properties.
    """
    host = "example.smtp"
    port = 25
    user = "example_user"
    password = "somepassword"  # nosec
    auth_type = "plain"
    transport_security = "tls"
    domain = "domain"
    charm = MagicMock(
        config={
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "auth_type": auth_type,
            "transport_security": transport_security,
            "domain": domain,
        }
    )
    state = CharmState.from_charm(charm)
    assert state.host == host
    assert state.port == port
    assert state.user == user
    assert state.password == password
    assert state.auth_type == auth_type
    assert state.transport_security == transport_security
    assert state.domain == domain


def test_charm_state_from_charm_with_invalid_config():
    """
    arrange: set up an unconfigured charm
    act: access the status properties
    assert: a CharmConfigInvalidError is raised.
    """
    charm = MagicMock(config={})
    with pytest.raises(CharmConfigInvalidError):
        CharmState.from_charm(charm)
