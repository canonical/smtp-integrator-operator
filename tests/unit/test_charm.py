# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

"""Unit tests."""
# pylint: disable=protected-access
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
    act: trigger a configuration change missing required configs.
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
    act: trigger a configuration change missing required configs.
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
    act: trigger a configuration change missing required configs.
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
    harness.update_config(
        {
            "host": host,
            "port": port,
        }
    )
    harness.begin()
    harness.charm.on.config_changed.emit()
    assert harness.model.unit.status == ops.ActiveStatus()
    harness.add_relation("smtp-legacy", "indico")
    data = harness.model.get_relation("smtp-legacy").data[harness.model.app]
    assert data["host"] == harness.charm._charm_state.host
    assert data["port"] == str(harness.charm._charm_state.port)


def test_relation_joined_when_leader():
    """
    arrange: set up a configured charm and set leadership for the unit.
    act: add a relation.
    assert: the relation gets populated with the SMTP data.
    """
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
    assert harness.model.unit.status == ops.ActiveStatus()
    harness.add_relation("smtp", "indico")
    data = harness.model.get_relation("smtp").data[harness.model.app]
    assert data["host"] == harness.charm._charm_state.host
    assert data["port"] == str(harness.charm._charm_state.port)


def test_legacy_relation_joined_when_not_leader():
    """
    arrange: set up a charm and unset leadership for the unit.
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
    assert harness.model.unit.status == ops.ActiveStatus()
    harness.add_relation("smtp-legacy", "indico")
    data = harness.model.get_relation("smtp-legacy").data[harness.model.app]
    assert data == {}


def test_relation_joined_when_not_leader():
    """
    arrange: set up a charm and unset leadership for the unit.
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
    assert harness.model.unit.status == ops.ActiveStatus()
    harness.add_relation("smtp", "indico")
    data = harness.model.get_relation("smtp").data[harness.model.app]
    assert data == {}
