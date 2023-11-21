# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

"""Unit tests."""
# pylint: disable=protected-access
from unittest.mock import MagicMock, patch

import ops
from ops.testing import Harness

from charm import SmtpIntegratorOperatorCharm


def test_unconfigured_charm_reaches_blocked_status():
    """
    arrange: set up a charm.
    act: trigger a configuration change missing required configs.
    assert: the charm reaches BlockedStatus.
    """
    harness = Harness(SmtpIntegratorOperatorCharm)
    harness.begin()
    assert harness.model.unit.status.name == ops.BlockedStatus().name


def test_misconfigured_port_charm_reaches_blocked_status():
    """
    arrange: set up a charm.
    act: trigger a configuration change with an invalid port.
    assert: the charm reaches BlockedStatus.
    """
    harness = Harness(SmtpIntegratorOperatorCharm)
    harness.update_config(
        {
            "host": "smtp.example",
            "port": 0,
        }
    )
    harness.begin()
    assert harness.model.unit.status.name == ops.BlockedStatus().name


def test_misconfigured_auth_type_charm_reaches_blocked_status():
    """
    arrange: set up a charm.
    act: trigger a configuration change with an invalid auth type.
    assert: the charm reaches BlockedStatus.
    """
    harness = Harness(SmtpIntegratorOperatorCharm)
    harness.update_config(
        {
            "host": "smtp.example",
            "port": 25,
            "auth_type": "nonexisting",
        }
    )
    harness.begin()
    assert harness.model.unit.status.name == ops.BlockedStatus().name


def test_misconfigured_transport_security_charm_reaches_blocked_status():
    """
    arrange: set up a charm.
    act: trigger a configuration change with an invalid transport security.
    assert: the charm reaches BlockedStatus.
    """
    harness = Harness(SmtpIntegratorOperatorCharm)
    harness.update_config(
        {
            "host": "smtp.example",
            "port": 25,
            "transport_security": "nonexisting",
        }
    )
    harness.begin()
    assert harness.model.unit.status.name == ops.BlockedStatus().name


def test_charm_reaches_active_status():
    """
    arrange: set up a charm.
    act: trigger a configuration change with the required configs.
    assert: the charm reaches ActiveStatus.
    """
    harness = Harness(SmtpIntegratorOperatorCharm)
    harness.update_config(
        {
            "host": "smtp.example",
            "port": 25,
        }
    )
    harness.begin()
    harness.charm.on.config_changed.emit()
    assert harness.model.unit.status == ops.ActiveStatus()


def test_legacy_relation_joined_when_leader():
    """
    arrange: set up a configured charm and set leadership for the unit.
    act: add a relation.
    assert: the relation gets populated with the SMTP data.
    """
    harness = Harness(SmtpIntegratorOperatorCharm)
    harness.set_leader(True)
    host = "smtp.example"
    port = 25
    password = "somepassword"  # nosec
    harness.update_config(
        {
            "host": host,
            "port": port,
            "password": password,
        }
    )
    harness.begin()
    harness.charm.on.config_changed.emit()
    harness.add_relation("smtp-legacy", "example")
    data = harness.model.get_relation("smtp-legacy").data[harness.model.app]
    assert data["host"] == host
    assert data["port"] == str(port)
    assert data["password"] == password
    assert "password_id" not in data


@patch.object(ops.JujuVersion, "from_environ")
def test_relation_joined_when_leader_and_secrets(mock_juju_env):
    """
    arrange: set up a configured charm mimicking Juju 3 and set leadership for the unit.
    act: add a relation.
    assert: the relation gets populated with the SMTP data.
    """
    mock_juju_env.return_value = MagicMock(has_secrets=True)
    harness = Harness(SmtpIntegratorOperatorCharm)
    harness.set_leader(True)
    host = "smtp.example"
    port = 25
    password = "somepassword"  # nosec
    harness.update_config(
        {
            "host": host,
            "port": port,
            "password": password,
        }
    )
    harness.begin()
    harness.charm.on.config_changed.emit()
    harness.add_relation("smtp", "example")
    data = harness.model.get_relation("smtp").data[harness.model.app]
    assert data["host"] == host
    assert data["port"] == str(port)
    assert "password" not in data
    assert data["password_id"] is not None


@patch.object(ops.JujuVersion, "from_environ")
def test_relation_joined_when_leader_and_no_secrets(mock_juju_env):
    """
    arrange: set up a configured charm mimicking Juju 2 and set leadership for the unit.
    act: add a relation.
    assert: the relation does not get populated with the SMTP data.
    """
    mock_juju_env.return_value = MagicMock(has_secrets=False)
    harness = Harness(SmtpIntegratorOperatorCharm)
    harness.set_leader(True)
    host = "smtp.example"
    port = 25
    password = "somepassword"  # nosec
    harness.update_config(
        {
            "host": host,
            "port": port,
            "password": password,
        }
    )
    harness.begin()
    harness.charm.on.config_changed.emit()
    harness.add_relation("smtp", "example")
    data = harness.model.get_relation("smtp").data[harness.model.app]
    assert data == {}


@patch.object(ops.JujuVersion, "from_environ")
def test_relation_joined_when_leader_and_no_password(mock_juju_env):
    """
    arrange: set up a configured charm mimicking Juju 3 and set leadership for the unit.
    act: add a relation.
    assert: the relation gets populated with the SMTP data.
    """
    mock_juju_env.return_value = MagicMock(has_secrets=True)
    harness = Harness(SmtpIntegratorOperatorCharm)
    harness.set_leader(True)
    host = "smtp.example"
    port = 25
    harness.update_config(
        {
            "host": host,
            "port": port,
        }
    )
    harness.begin()
    harness.charm.on.config_changed.emit()
    harness.add_relation("smtp", "example")
    data = harness.model.get_relation("smtp").data[harness.model.app]
    assert data["host"] == host
    assert data["port"] == str(port)
    assert "password" not in data
    assert "password_id" not in data


def test_legacy_relation_joined_when_not_leader():
    """
    arrange: set up a charm mimicking Juju 3 and unset leadership for the unit.
    act: add a relation.
    assert: the relation does not get populated with the SMTP data.
    """
    harness = Harness(SmtpIntegratorOperatorCharm)
    harness.set_leader(False)
    host = "smtp.example"
    port = 25
    harness.update_config(
        {
            "host": host,
            "port": port,
        }
    )
    harness.begin()
    harness.charm.on.config_changed.emit()
    harness.add_relation("smtp-legacy", "example")
    data = harness.model.get_relation("smtp-legacy").data[harness.model.app]
    assert data == {}


@patch.object(ops.JujuVersion, "from_environ")
def test_relation_joined_when_not_leader(mock_juju_env):
    """
    arrange: set up a charm mimicking Juju 3 and unset leadership for the unit.
    act: add a relation.
    assert: the relation does not get populated with the SMTP data.
    """
    mock_juju_env.return_value = MagicMock(has_secrets=True)
    harness = Harness(SmtpIntegratorOperatorCharm)
    harness.set_leader(False)
    host = "smtp.example"
    port = 25
    harness.update_config(
        {
            "host": host,
            "port": port,
        }
    )
    harness.begin()
    harness.charm.on.config_changed.emit()
    harness.add_relation("smtp", "example")
    data = harness.model.get_relation("smtp").data[harness.model.app]
    assert data == {}
