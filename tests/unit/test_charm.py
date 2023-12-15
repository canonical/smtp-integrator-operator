# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

"""Unit tests."""

import secrets
from unittest.mock import MagicMock, patch

import ops
from ops.testing import Harness

from charm import SmtpIntegratorOperatorCharm

MINIMAL_CHARM_CONFIG = {
    "host": "smtp.example",
    "port": 25,
}
MINIMAL_CHARM_CONFIG_WITH_PASSWORD = {
    **MINIMAL_CHARM_CONFIG,
    "password": secrets.token_hex(),
}


def test_unconfigured_charm_reaches_blocked_status():
    """
    arrange: set up a charm without configuration.
    act: none
    assert: the charm reaches BlockedStatus.
    """
    harness = Harness(SmtpIntegratorOperatorCharm)
    harness.begin()
    assert harness.model.unit.status.name == ops.BlockedStatus().name


def test_misconfigured_port_charm_reaches_blocked_status():
    """
    arrange: set up a charm with an invalid port.
    act: none
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
    arrange: set up a charm ith an invalid auth type.
    act: none
    assert: the charm reaches BlockedStatus.
    """
    harness = Harness(SmtpIntegratorOperatorCharm)
    harness.update_config(
        {
            **MINIMAL_CHARM_CONFIG,
            "auth_type": "nonexisting",
        }
    )
    harness.begin()
    assert harness.model.unit.status.name == ops.BlockedStatus().name


def test_misconfigured_transport_security_charm_reaches_blocked_status():
    """
    arrange: set up a charm with an invalid transport security.
    act: none
    assert: the charm reaches BlockedStatus.
    """
    harness = Harness(SmtpIntegratorOperatorCharm)
    harness.update_config(
        {
            **MINIMAL_CHARM_CONFIG,
            "transport_security": "nonexisting",
        }
    )
    harness.begin()
    assert harness.model.unit.status.name == ops.BlockedStatus().name


def test_charm_reaches_active_status():
    """
    arrange: set up a charm with minimal valid configuration.
    act: trigger a configuration change with the required configs.
    assert: the charm reaches ActiveStatus.
    """
    harness = Harness(SmtpIntegratorOperatorCharm)
    harness.update_config(MINIMAL_CHARM_CONFIG)
    harness.begin()
    harness.charm.on.config_changed.emit()
    assert harness.model.unit.status == ops.ActiveStatus()


def test_legacy_relation_joined_populates_data():
    """
    arrange: set up a charm with valid configuration and leadership for the unit.
    act: add an smtp-legacy relation.
    assert: the smtp-legacy relation gets populated with the SMTP data.
    """
    harness = Harness(SmtpIntegratorOperatorCharm)
    harness.set_leader(True)
    harness.update_config(MINIMAL_CHARM_CONFIG_WITH_PASSWORD)
    harness.begin()
    harness.charm.on.config_changed.emit()
    harness.add_relation("smtp-legacy", "example")
    data = harness.model.get_relation("smtp-legacy").data[harness.model.app]
    assert data["host"] == MINIMAL_CHARM_CONFIG_WITH_PASSWORD["host"]
    assert data["port"] == str(MINIMAL_CHARM_CONFIG_WITH_PASSWORD["port"])
    assert data["password"] == MINIMAL_CHARM_CONFIG_WITH_PASSWORD["password"]


def test_legacy_relation_joined_doesnt_populate_password_id():
    """
    arrange: set up a charm with valid configuration and leadership for the unit.
    act: add an smtp-legacy relation.
    assert: the smtp-legacy relation does not get populated with the password_id.
    """
    harness = Harness(SmtpIntegratorOperatorCharm)
    harness.set_leader(True)
    harness.update_config(MINIMAL_CHARM_CONFIG_WITH_PASSWORD)
    harness.begin()
    harness.charm.on.config_changed.emit()
    harness.add_relation("smtp-legacy", "example")
    data = harness.model.get_relation("smtp-legacy").data[harness.model.app]
    assert "password_id" not in data


@patch.object(ops.JujuVersion, "from_environ")
def test_relation_joined_when_secrets_enabled_populates_data(mock_juju_env):
    """
    arrange: set up a charm with valid configuration mimicking Juju 3 and leadership for the unit.
    act: add an smtp relation.
    assert: the smtp relation gets populated with the SMTP data.
    """
    mock_juju_env.return_value = MagicMock(has_secrets=True)
    harness = Harness(SmtpIntegratorOperatorCharm)
    harness.set_leader(True)
    harness.update_config(MINIMAL_CHARM_CONFIG_WITH_PASSWORD)
    harness.begin()
    harness.add_relation("smtp-peers", harness.charm.app.name)
    harness.charm.on.config_changed.emit()
    harness.add_relation("smtp", "example")
    data = harness.model.get_relation("smtp").data[harness.model.app]
    assert data["host"] == MINIMAL_CHARM_CONFIG_WITH_PASSWORD["host"]
    assert data["port"] == str(MINIMAL_CHARM_CONFIG_WITH_PASSWORD["port"])
    assert data["password_id"] is not None


@patch.object(ops.JujuVersion, "from_environ")
def test_relation_joined_when_secrets_enabled_doesnt_populate_password(mock_juju_env):
    """
    arrange: set up a charm with valid configuration mimicking Juju 3 and leadership for the unit.
    act: add an smtp relation.
    assert: the smtp relation does not populate with the password.
    """
    mock_juju_env.return_value = MagicMock(has_secrets=True)
    harness = Harness(SmtpIntegratorOperatorCharm)
    harness.set_leader(True)
    harness.update_config(MINIMAL_CHARM_CONFIG_WITH_PASSWORD)
    harness.begin()
    harness.add_relation("smtp-peers", harness.charm.app.name)
    harness.charm.on.config_changed.emit()
    harness.add_relation("smtp", "example")
    data = harness.model.get_relation("smtp").data[harness.model.app]
    assert "password" not in data


@patch.object(ops.JujuVersion, "from_environ")
def test_relation_joined_when_no_secrets_enabled(mock_juju_env):
    """
    arrange: set up a charm with valid configuration mimicking Juju 2 and leadership for the unit.
    act: add an smtp relation.
    assert: the smtp relation does not get populated with the SMTP data.
    """
    mock_juju_env.return_value = MagicMock(has_secrets=False)
    harness = Harness(SmtpIntegratorOperatorCharm)
    harness.set_leader(True)
    harness.update_config(MINIMAL_CHARM_CONFIG_WITH_PASSWORD)
    harness.begin()
    harness.charm.on.config_changed.emit()
    harness.add_relation("smtp", "example")
    data = harness.model.get_relation("smtp").data[harness.model.app]
    assert data == {}


@patch.object(ops.JujuVersion, "from_environ")
def test_relation_joined_when_no_password_configured(mock_juju_env):
    """
    arrange: set up a configured charm mimicking Juju 3 and leadership for the unit.
    act: add an smtp relation.
    assert: the relation gets populated with the SMTP data and the password_id is not present.
    """
    mock_juju_env.return_value = MagicMock(has_secrets=True)
    harness = Harness(SmtpIntegratorOperatorCharm)
    harness.set_leader(True)
    harness.update_config(MINIMAL_CHARM_CONFIG)
    harness.begin()
    harness.add_relation("smtp-peers", harness.charm.app.name)
    harness.charm.on.config_changed.emit()
    harness.add_relation("smtp", "example")
    data = harness.model.get_relation("smtp").data[harness.model.app]
    assert data["host"] == MINIMAL_CHARM_CONFIG["host"]
    assert data["port"] == str(MINIMAL_CHARM_CONFIG["port"])
    assert "password" not in data
    assert "password_id" not in data


def test_legacy_relation_joined_when_not_leader():
    """
    arrange: set up a charm mimicking Juju 3 and unset leadership for the unit.
    act: add an smtp-legacy relation.
    assert: the smtp-legacy relation does not get populated with the SMTP data.
    """
    harness = Harness(SmtpIntegratorOperatorCharm)
    harness.set_leader(False)
    harness.update_config(MINIMAL_CHARM_CONFIG)
    harness.begin()
    harness.add_relation("smtp-peers", harness.charm.app.name)
    harness.charm.on.config_changed.emit()
    harness.add_relation("smtp-legacy", "example")
    data = harness.model.get_relation("smtp-legacy").data[harness.model.app]
    assert data == {}


@patch.object(ops.JujuVersion, "from_environ")
def test_relation_joined_when_not_leader(mock_juju_env):
    """
    arrange: set up a charm mimicking Juju 3 and unset leadership for the unit.
    act: add an smtp relation.
    assert: the smtp relation does not get populated with the SMTP data.
    """
    mock_juju_env.return_value = MagicMock(has_secrets=True)
    harness = Harness(SmtpIntegratorOperatorCharm)
    harness.set_leader(False)
    harness.update_config(MINIMAL_CHARM_CONFIG)
    harness.begin()
    harness.charm.on.config_changed.emit()
    harness.add_relation("smtp", "example")
    data = harness.model.get_relation("smtp").data[harness.model.app]
    assert data == {}
