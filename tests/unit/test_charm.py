# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Unit tests."""

import json
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

MINIMAL_CHARM_CONFIG_WITH_EMAILS = {
    **MINIMAL_CHARM_CONFIG,
    "smtp_sender": "no-reply@example.com",
    "recipients": "a@x.com,b@y.com",
}

MINIMAL_CHARM_CONFIG_WITH_EMAILS_SPACES = {
    **MINIMAL_CHARM_CONFIG,
    "smtp_sender": "no-reply@example.com",
    "recipients": "a@x.com, b@y.com  ,  c@z.com",
}


def test_unconfigured_charm_reaches_blocked_status():
    """
    arrange: set up a charm without configuration.
    act: none
    assert: the charm reaches BlockedStatus.
    """
    harness = Harness(SmtpIntegratorOperatorCharm)
    harness.set_leader(True)
    harness.begin_with_initial_hooks()
    assert harness.model.unit.status.name == ops.BlockedStatus().name


def test_misconfigured_port_charm_reaches_blocked_status():
    """
    arrange: set up a charm with an invalid port.
    act: none
    assert: the charm reaches BlockedStatus.
    """
    harness = Harness(SmtpIntegratorOperatorCharm)
    harness.set_leader(True)
    harness.update_config(
        {
            "host": "smtp.example",
            "port": 0,
        }
    )
    harness.begin_with_initial_hooks()
    assert harness.model.unit.status.name == ops.BlockedStatus().name


def test_misconfigured_auth_type_charm_reaches_blocked_status():
    """
    arrange: set up a charm ith an invalid auth type.
    act: none
    assert: the charm reaches BlockedStatus.
    """
    harness = Harness(SmtpIntegratorOperatorCharm)
    harness.set_leader(True)
    harness.update_config(
        {
            **MINIMAL_CHARM_CONFIG,
            "auth_type": "nonexisting",
        }
    )
    harness.begin_with_initial_hooks()
    assert harness.model.unit.status.name == ops.BlockedStatus().name


def test_misconfigured_transport_security_charm_reaches_blocked_status():
    """
    arrange: set up a charm with an invalid transport security.
    act: none
    assert: the charm reaches BlockedStatus.
    """
    harness = Harness(SmtpIntegratorOperatorCharm)
    harness.set_leader(True)
    harness.update_config(
        {
            **MINIMAL_CHARM_CONFIG,
            "transport_security": "nonexisting",
        }
    )
    harness.begin_with_initial_hooks()
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
    harness.begin_with_initial_hooks()
    harness.add_relation("smtp-legacy", "example")
    data = harness.model.get_relation("smtp-legacy").data[harness.model.app]
    assert data["host"] == MINIMAL_CHARM_CONFIG_WITH_PASSWORD["host"]
    assert data["port"] == str(MINIMAL_CHARM_CONFIG_WITH_PASSWORD["port"])
    assert data["password"] == MINIMAL_CHARM_CONFIG_WITH_PASSWORD["password"]


def test_config_changed_joined_populates_data():
    """
    arrange: set up a charm with valid configuration and leadership for the unit.
    act: add an smtp-legacy relation and trigger a configuration change.
    assert: the smtp-legacy relation gets populated with the SMTP data.
    """
    harness = Harness(SmtpIntegratorOperatorCharm)
    harness.set_leader(True)
    harness.update_config(MINIMAL_CHARM_CONFIG_WITH_PASSWORD)
    harness.begin_with_initial_hooks()
    harness.add_relation("smtp-legacy", "example")
    harness.charm.on.config_changed.emit()
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
    harness.add_relation("smtp", "example")
    data = harness.model.get_relation("smtp").data[harness.model.app]
    assert data["host"] == MINIMAL_CHARM_CONFIG_WITH_PASSWORD["host"]
    assert data["port"] == str(MINIMAL_CHARM_CONFIG_WITH_PASSWORD["port"])
    assert data["password_id"] is not None


@patch.object(ops.JujuVersion, "from_environ")
def test_config_changed_when_secrets_enabled_populates_data(mock_juju_env):
    """
    arrange: set up a charm with valid configuration mimicking Juju 3 and leadership for the unit.
    act: add an smtp relation and trigger a configuration change.
    assert: the smtp relation gets populated with the SMTP data.
    """
    mock_juju_env.return_value = MagicMock(has_secrets=True)
    harness = Harness(SmtpIntegratorOperatorCharm)
    harness.set_leader(True)
    harness.update_config(MINIMAL_CHARM_CONFIG_WITH_PASSWORD)
    harness.begin()
    harness.add_relation("smtp-peers", harness.charm.app.name)
    harness.add_relation("smtp", "example")
    harness.charm.on.config_changed.emit()
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
    harness.add_relation("smtp-peers", harness.charm.app.name)
    harness.charm.on.config_changed.emit()
    harness.add_relation("smtp", "example")
    data = harness.model.get_relation("smtp").data[harness.model.app]
    assert data == {}


@patch.object(ops.JujuVersion, "from_environ")
def test_smtp_relation_in_juju_2(mock_juju_env):
    """
    arrange: set up a charm in Juju 2 environment.
    act: add a smtp relation.
    assert: the charm should enter blocked state.
    """
    mock_juju_env.return_value = MagicMock(has_secrets=False)
    harness = Harness(SmtpIntegratorOperatorCharm)
    harness.set_leader(True)
    harness.update_config(MINIMAL_CHARM_CONFIG)
    harness.begin()
    harness.add_relation("smtp-peers", harness.charm.app.name)
    harness.charm.on.config_changed.emit()
    harness.add_relation("smtp", "example")
    assert harness.charm.unit.status.name == "blocked"


@patch.object(ops.JujuVersion, "from_environ")
def test_provider_charm_update_secret_content(mock_juju_env):
    """
    arrange: relate the smtp-consumer charm with a provider charm.
    act: update the password configuration in the provider charm.
    assert: secret content in the relation data should be updated.
    """
    mock_juju_env.return_value = MagicMock(has_secrets=True)
    harness = Harness(SmtpIntegratorOperatorCharm)
    harness.begin_with_initial_hooks()
    harness.set_leader(True)
    relation_id = harness.add_relation("smtp", "smtp-requirer")
    harness.update_config(
        {
            "host": "example.smtp",
            "port": 25,
            "user": "example_user",
            "auth_type": "plain",
            "password": "foo",  # nosec B105
            "domain": "example.smtp",
        }
    )
    relation_data = harness.get_relation_data(
        relation_id=relation_id, app_or_unit=harness.charm.app
    )
    assert "password" not in relation_data
    password_id = relation_data["password_id"]
    assert harness.get_secret_grants(password_id, relation_id) == {"smtp-requirer"}
    secret_content = harness.model.get_secret(id=password_id).get_content(refresh=True)
    assert secret_content == {"password": "foo"}  # nosec B105

    harness.update_config(
        {
            "password": "bar",  # nosec B105
        }
    )
    relation_data = harness.get_relation_data(
        relation_id=relation_id, app_or_unit=harness.charm.app
    )
    assert password_id == relation_data["password_id"]
    secret_content = harness.model.get_secret(id=password_id).get_content(refresh=True)
    assert secret_content == {"password": "bar"}  # nosec B105


@patch.object(ops.JujuVersion, "from_environ")
def test_provider_charm_revoke_secret_on_broken(mock_juju_env):
    """
    arrange: relate the smtp-consumer charm with a provider charm.
    act: remove the smtp relation.
    assert: secrets inside the smtp relation should be removed.
    """
    mock_juju_env.return_value = MagicMock(has_secrets=True)
    harness = Harness(SmtpIntegratorOperatorCharm)
    harness.begin_with_initial_hooks()
    harness.set_leader(True)
    relation_id = harness.add_relation("smtp", "smtp-requirer")
    harness.update_config(
        {
            "host": "example.smtp",
            "port": 25,
            "user": "example_user",
            "auth_type": "plain",
            "password": "foo",  # nosec B105
            "domain": "example.smtp",
        }
    )
    relation_data = harness.get_relation_data(
        relation_id=relation_id, app_or_unit=harness.charm.app
    )
    password_id = relation_data["password_id"]
    assert "smtp-requirer" in harness.get_secret_grants(password_id, relation_id)

    harness.remove_relation(relation_id)

    assert "smtp-requirer" not in harness.get_secret_grants(password_id, relation_id)


@patch.object(ops.JujuVersion, "from_environ")
def test_provider_charm_update_secret_revision(mock_juju_env):
    """
    arrange: relate the smtp-consumer charm with a provider charm.
    act: update the charm configuration in the provider charm.
    assert: secret revision in the relation data should remain unchanged.
    """
    mock_juju_env.return_value = MagicMock(has_secrets=True)
    harness = Harness(SmtpIntegratorOperatorCharm)
    harness.begin_with_initial_hooks()
    harness.set_leader(True)
    relation_id = harness.add_relation("smtp", "smtp-requirer")
    harness.update_config(
        {
            "host": "example.smtp",
            "port": 25,
            "user": "example_user",
            "auth_type": "plain",
            "password": "foo",  # nosec B105
            "domain": "example.smtp",
        }
    )
    relation_data = harness.get_relation_data(
        relation_id=relation_id, app_or_unit=harness.charm.app
    )
    password_id = relation_data["password_id"]
    assert len(harness.get_secret_revisions(password_id)) == 1

    harness.update_config(
        {
            "domain": "smtp.example",
        }
    )
    assert len(harness.get_secret_revisions(password_id)) == 1


def test_smtp_sender_when_misconfigured_then_charm_reaches_blocked_status():
    """
    arrange: set up a charm with smtp_sender with invalid smtp_sender configuration.
    act: None
    assert: the charm reaches BlockedStatus.
    """
    harness = Harness(SmtpIntegratorOperatorCharm)
    harness.set_leader(True)
    harness.update_config(
        {
            **MINIMAL_CHARM_CONFIG,
            "smtp_sender": "not-an-email",
        }
    )
    harness.begin_with_initial_hooks()
    assert harness.model.unit.status.name == ops.BlockedStatus().name


def test_smtp_sender_when_configured_then_charm_reaches_active_status():
    """
    arrange: set up a charm with valid smtp_sender and minimal config.
    act: emit config_changed.
    assert: the charm reaches ActiveStatus.
    """
    harness = Harness(SmtpIntegratorOperatorCharm)
    harness.update_config(
        {
            **MINIMAL_CHARM_CONFIG,
            "smtp_sender": "no-reply@example.com",
        }
    )
    harness.begin()
    harness.charm.on.config_changed.emit()
    assert harness.model.unit.status == ops.ActiveStatus()


def test_recipients_when_misconfigured_then_charm_reaches_blocked_status():
    """
    arrange: set up a charm with recipients containing an invalid email.
    act: none
    assert: the charm reaches BlockedStatus.
    """
    harness = Harness(SmtpIntegratorOperatorCharm)
    harness.set_leader(True)
    harness.update_config(
        {
            **MINIMAL_CHARM_CONFIG,
            "recipients": "a@x.com,not-an-email",
        }
    )
    harness.begin_with_initial_hooks()
    assert harness.model.unit.status.name == ops.BlockedStatus().name


def test_recipients_when_configured_then_charm_reaches_active_status():
    """
    arrange: set up a charm with valid recipients and minimal config.
    act: emit config_changed.
    assert: the charm reaches ActiveStatus.
    """
    harness = Harness(SmtpIntegratorOperatorCharm)
    harness.update_config(
        {
            **MINIMAL_CHARM_CONFIG,
            "recipients": "a@x.com,b@y.com",
        }
    )
    harness.begin()
    harness.charm.on.config_changed.emit()
    assert harness.model.unit.status == ops.ActiveStatus()


def test_legacy_relation_joined_when_sender_or_recipients_configured_then_populates():
    """
    arrange: set up a charm with valid smtp_sender and recipients.
    act: add smtp-legacy relation.
    assert: relation data includes smtp_sender and recipients as JSON list string.
    """
    harness = Harness(SmtpIntegratorOperatorCharm)
    harness.set_leader(True)
    harness.update_config(
        {**MINIMAL_CHARM_CONFIG_WITH_PASSWORD, **MINIMAL_CHARM_CONFIG_WITH_EMAILS}
    )
    harness.begin_with_initial_hooks()

    harness.add_relation("smtp-legacy", "example")
    data = harness.model.get_relation("smtp-legacy").data[harness.model.app]

    assert data["smtp_sender"] == "no-reply@example.com"
    assert json.loads(data["recipients"]) == ["a@x.com", "b@y.com"]


def test_legacy_relation_joined_when_sender_or_recipients_unset_then_does_not_publish():
    """
    arrange: charm with minimal config only.
    act: add smtp-legacy relation.
    assert: smtp_sender and recipients keys are not present.
    """
    harness = Harness(SmtpIntegratorOperatorCharm)
    harness.set_leader(True)
    harness.update_config(MINIMAL_CHARM_CONFIG_WITH_PASSWORD)
    harness.begin_with_initial_hooks()

    harness.add_relation("smtp-legacy", "example")
    data = harness.model.get_relation("smtp-legacy").data[harness.model.app]

    assert "smtp_sender" not in data
    assert "recipients" not in data
