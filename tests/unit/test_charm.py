# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Unit tests."""

import json
import secrets
from typing import cast

import ops
from scenario import Context, PeerRelation, Relation, Secret, State

from tests.unit.conftest import (
    MINIMAL_CHARM_CONFIG,
    MINIMAL_CHARM_CONFIG_WITH_EMAILS,
    MINIMAL_CHARM_CONFIG_WITH_PASSWORD,
)


def test_unconfigured_charm_reaches_blocked_status(context: Context):
    """
    arrange: set up a charm without configuration.
    act: trigger config_changed event.
    assert: the charm reaches BlockedStatus.
    """
    state_in = State(leader=True)
    state_out = context.run(context.on.config_changed(), state_in)
    assert state_out.unit_status.name == ops.BlockedStatus().name


def test_misconfigured_port_charm_reaches_blocked_status(context: Context):
    """
    arrange: set up a charm with an invalid port.
    act: trigger config_changed event.
    assert: the charm reaches BlockedStatus.
    """
    state_in = State(
        leader=True,
        config={
            "host": "smtp.example",
            "port": 0,
        },
    )
    state_out = context.run(context.on.config_changed(), state_in)
    assert state_out.unit_status.name == ops.BlockedStatus().name


def test_misconfigured_auth_type_charm_reaches_blocked_status(context: Context):
    """
    arrange: set up a charm with an invalid auth type.
    act: trigger config_changed event.
    assert: the charm reaches BlockedStatus.
    """
    state_in = State(
        leader=True,
        config={
            "host": "smtp.example",
            "port": 25,
            "auth_type": "nonexisting",
        },
    )
    state_out = context.run(context.on.config_changed(), state_in)
    assert state_out.unit_status.name == ops.BlockedStatus().name


def test_misconfigured_transport_security_charm_reaches_blocked_status(context: Context):
    """
    arrange: set up a charm with an invalid transport security.
    act: trigger config_changed event.
    assert: the charm reaches BlockedStatus.
    """
    state_in = State(
        leader=True,
        config={
            "host": "smtp.example",
            "port": 25,
            "transport_security": "nonexisting",
        },
    )
    state_out = context.run(context.on.config_changed(), state_in)
    assert state_out.unit_status.name == ops.BlockedStatus().name


def test_charm_reaches_active_status(context: Context):
    """
    arrange: set up a charm with minimal valid configuration.
    act: trigger a configuration change with the required configs.
    assert: the charm reaches ActiveStatus.
    """
    state_in = State(
        config={
            "host": "smtp.example",
            "port": 25,
        }
    )
    state_out = context.run(context.on.config_changed(), state_in)
    assert state_out.unit_status == ops.ActiveStatus()


def test_legacy_relation_joined_populates_data(context: Context):
    """
    arrange: set up a charm with valid configuration and leadership for the unit, and a relation.
    act: trigger config_changed event.
    assert: the smtp-legacy relation gets populated with the SMTP data.
    """
    peer_relation = PeerRelation(endpoint="smtp-peers")
    relation = Relation(endpoint="smtp-legacy", remote_app_name="example")
    state_in = State(
        leader=True,
        config=cast(dict[str, str | int | float | bool], MINIMAL_CHARM_CONFIG_WITH_PASSWORD),
        relations=[peer_relation, relation],
    )
    state_out = context.run(context.on.config_changed(), state_in)
    data = state_out.get_relation(relation.id).local_app_data
    assert data is not None
    assert data["host"] == MINIMAL_CHARM_CONFIG_WITH_PASSWORD["host"]
    assert data["port"] == str(MINIMAL_CHARM_CONFIG_WITH_PASSWORD["port"])
    assert data["password"] == MINIMAL_CHARM_CONFIG_WITH_PASSWORD["password"]


def test_config_changed_joined_populates_data(context: Context):
    """
    arrange: set up a charm with valid configuration and leadership for the unit.
    act: add an smtp-legacy relation and trigger a configuration change.
    assert: the smtp-legacy relation gets populated with the SMTP data.
    """
    peer_relation = PeerRelation(endpoint="smtp-peers")
    relation = Relation(endpoint="smtp-legacy", remote_app_name="example")
    state_in = State(
        leader=True,
        config=cast(dict[str, str | int | float | bool], MINIMAL_CHARM_CONFIG_WITH_PASSWORD),
        relations=[peer_relation, relation],
    )
    state_out = context.run(context.on.config_changed(), state_in)
    data = state_out.get_relation(relation.id).local_app_data
    assert data is not None
    assert data["host"] == MINIMAL_CHARM_CONFIG_WITH_PASSWORD["host"]
    assert data["port"] == str(MINIMAL_CHARM_CONFIG_WITH_PASSWORD["port"])
    assert data["password"] == MINIMAL_CHARM_CONFIG_WITH_PASSWORD["password"]


def test_legacy_relation_joined_doesnt_populate_password_id(context: Context):
    """
    arrange: set up a charm with valid configuration and leadership for the unit.
    act: trigger config_changed with smtp-legacy relation present.
    assert: the smtp-legacy relation does not get populated with the password_id.
    """
    peer_relation = PeerRelation(endpoint="smtp-peers")
    relation = Relation(endpoint="smtp-legacy", remote_app_name="example")
    state_in = State(
        leader=True,
        config=cast(dict[str, str | int | float | bool], MINIMAL_CHARM_CONFIG_WITH_PASSWORD),
        relations=[peer_relation, relation],
    )
    state_out = context.run(context.on.config_changed(), state_in)
    data = state_out.get_relation(relation.id).local_app_data
    assert data is not None
    assert "password_id" not in data


def test_relation_joined(context: Context):
    """
    arrange: set up a charm with valid configuration mimicking Juju 3 and leadership for the unit.
    act: trigger config_changed with smtp relation present.
    assert: the smtp relation gets populated with the SMTP data.
    """
    peer_relation = PeerRelation(endpoint="smtp-peers")
    relation = Relation(endpoint="smtp", remote_app_name="example")
    state_in = State(
        leader=True,
        config=cast(dict[str, str | int | float | bool], MINIMAL_CHARM_CONFIG_WITH_PASSWORD),
        relations=[peer_relation, relation],
    )
    state_out = context.run(context.on.config_changed(), state_in)
    data = state_out.get_relation(relation.id).local_app_data
    assert data is not None
    assert data["host"] == MINIMAL_CHARM_CONFIG_WITH_PASSWORD["host"]
    assert data["port"] == str(MINIMAL_CHARM_CONFIG_WITH_PASSWORD["port"])
    assert "password_id" in data
    assert data["password_id"] is not None


def test_config_changed(context: Context):
    """
    arrange: set up a charm with valid configuration mimicking Juju 3 and leadership for the unit.
    act: add an smtp relation and trigger a configuration change.
    assert: the smtp relation gets populated with the SMTP data.
    """
    peer_relation = PeerRelation(endpoint="smtp-peers")
    relation = Relation(endpoint="smtp", remote_app_name="example")
    state_in = State(
        leader=True,
        config=cast(dict[str, str | int | float | bool], MINIMAL_CHARM_CONFIG_WITH_PASSWORD),
        relations=[peer_relation, relation],
    )
    state_out = context.run(context.on.config_changed(), state_in)
    data = state_out.get_relation(relation.id).local_app_data
    assert data is not None
    assert data["host"] == MINIMAL_CHARM_CONFIG_WITH_PASSWORD["host"]
    assert data["port"] == str(MINIMAL_CHARM_CONFIG_WITH_PASSWORD["port"])
    assert "password_id" in data
    assert data["password_id"] is not None


def test_relation_joined_when_no_password(context: Context):
    """
    arrange: set up a charm with valid configuration mimicking Juju 3 and leadership for the unit.
    act: trigger config_changed with smtp relation present.
    assert: the smtp relation does not populate with the password.
    """
    peer_relation = PeerRelation(endpoint="smtp-peers")
    relation = Relation(endpoint="smtp", remote_app_name="example")
    state_in = State(
        leader=True,
        config=cast(dict[str, str | int | float | bool], MINIMAL_CHARM_CONFIG_WITH_PASSWORD),
        relations=[peer_relation, relation],
    )
    state_out = context.run(context.on.config_changed(), state_in)
    data = state_out.get_relation(relation.id).local_app_data
    assert data is not None
    assert "password" not in data


def test_relation_joined_when_no_password_configured(context: Context):
    """
    arrange: set up a configured charm mimicking Juju 3 and leadership for the unit.
    act: trigger config_changed with smtp relation present.
    assert: the relation gets populated with the SMTP data and the password_id is not present.
    """
    peer_relation = PeerRelation(endpoint="smtp-peers")
    relation = Relation(endpoint="smtp", remote_app_name="example")
    state_in = State(
        leader=True,
        config=cast(dict[str, str | int | float | bool], MINIMAL_CHARM_CONFIG),
        relations=[peer_relation, relation],
    )
    state_out = context.run(context.on.config_changed(), state_in)
    data = state_out.get_relation(relation.id).local_app_data
    assert data is not None
    assert data["host"] == MINIMAL_CHARM_CONFIG["host"]
    assert data["port"] == str(MINIMAL_CHARM_CONFIG["port"])
    assert "password" not in data
    assert "password_id" not in data


def test_legacy_relation_joined_when_not_leader(context: Context):
    """
    arrange: set up a charm mimicking Juju 3 and unset leadership for the unit.
    act: trigger config_changed with smtp-legacy relation present.
    assert: the smtp-legacy relation does not get populated with the SMTP data.
    """
    peer_relation = PeerRelation(endpoint="smtp-peers")
    relation = Relation(endpoint="smtp-legacy", remote_app_name="example")
    state_in = State(
        leader=False,
        config=cast(dict[str, str | int | float | bool], MINIMAL_CHARM_CONFIG),
        relations=[peer_relation, relation],
    )
    state_out = context.run(context.on.config_changed(), state_in)
    data = state_out.get_relation(relation.id).local_app_data
    assert data == {}


def test_relation_joined_when_not_leader(context: Context):
    """
    arrange: set up a charm mimicking Juju 3 and unset leadership for the unit.
    act: trigger config_changed with smtp relation present.
    assert: the smtp relation does not get populated with the SMTP data.
    """
    peer_relation = PeerRelation(endpoint="smtp-peers")
    relation = Relation(endpoint="smtp", remote_app_name="example")
    state_in = State(
        leader=False,
        config=cast(dict[str, str | int | float | bool], MINIMAL_CHARM_CONFIG),
        relations=[peer_relation, relation],
    )
    state_out = context.run(context.on.config_changed(), state_in)
    data = state_out.get_relation(relation.id).local_app_data
    assert data == {}


def test_provider_charm_update_secret_content(context: Context):  # pylint: disable=too-many-locals
    """
    arrange: relate the smtp-consumer charm with a provider charm.
    act: update the password configuration in the provider charm.
    assert: secret content in the relation data should be updated.
    """
    peer_relation = PeerRelation(endpoint="smtp-peers")
    relation = Relation(endpoint="smtp", remote_app_name="smtp-requirer")
    password = secrets.token_hex()

    state_in = State(
        leader=True,
        config={
            "host": "example.smtp",
            "port": 25,
            "user": "example_user",
            "auth_type": "plain",
            "password": password,
            "domain": "example.smtp",
        },
        relations=[peer_relation, relation],
    )
    state_out = context.run(context.on.config_changed(), state_in)

    relation_data = state_out.get_relation(relation.id).local_app_data
    assert relation_data is not None
    assert "password" not in relation_data
    password_id = relation_data["password_id"]
    assert password_id is not None

    # Check the secret content
    secret = state_out.get_secret(id=password_id)
    assert secret.latest_content == {"password": password}

    # Update password - need to preserve peer relation data and secrets
    password2 = secrets.token_hex()
    peer_out = state_out.get_relation(peer_relation.id)
    state_in2 = State(
        leader=True,
        config={
            "host": "example.smtp",
            "port": 25,
            "user": "example_user",
            "auth_type": "plain",
            "password": password2,
            "domain": "example.smtp",
        },
        relations=[
            PeerRelation(
                endpoint="smtp-peers",
                local_app_data=peer_out.local_app_data,
            ),
            relation,
        ],
        secrets=list(state_out.secrets),
    )
    state_out2 = context.run(context.on.config_changed(), state_in2)

    relation_data2 = state_out2.get_relation(relation.id).local_app_data
    assert relation_data2 is not None
    password_id2 = relation_data2["password_id"]
    # The charm should reuse the same secret ID
    assert password_id == password_id2
    secret2 = state_out2.get_secret(id=password_id2)
    assert secret2.latest_content == {"password": password2}


def test_provider_charm_invalid_password_secret(context: Context):
    """
    arrange: configure a provider charm with a password_secret that doesn't exist.
    act: update the password configuration in the provider charm.
    assert: the charm reaches blocked status.
    """
    peer_relation = PeerRelation(endpoint="smtp-peers")
    # Create a secret to get a valid ID, but don't add it to state
    temp_secret = Secret({"temp": "data"})
    state_in = State(
        leader=True,
        config={
            "host": "example.smtp",
            "port": 25,
            "user": "example_user",
            "auth_type": "plain",
            "password_secret": temp_secret.id,
            "domain": "example.smtp",
        },
        relations=[peer_relation],
        # No secrets in state - the secret doesn't exist
    )
    state_out = context.run(context.on.config_changed(), state_in)
    assert state_out.unit_status.name == ops.BlockedStatus().name


def test_provider_charm_invalid_password_secret_content(context: Context):
    """
    arrange: configure a provider charm with an invalid password_secret content.
    act: update the password configuration in the provider charm.
    assert: the charm reaches blocked status.
    """
    peer_relation = PeerRelation(endpoint="smtp-peers")
    secret = Secret(
        tracked_content={"invalid": "value"},
        label="password-secret",
        owner="app",
    )
    state_in = State(
        leader=True,
        config={
            "host": "example.smtp",
            "port": 25,
            "user": "example_user",
            "auth_type": "plain",
            "password_secret": secret.id,
            "domain": "example.smtp",
        },
        relations=[peer_relation],
        secrets=[secret],
    )
    state_out = context.run(context.on.config_changed(), state_in)
    assert state_out.unit_status.name == ops.BlockedStatus().name


def test_provider_charm_valid_secret_content(context: Context):
    """
    arrange: configure a charm with an valid password_secret and relate a consumer charm with it.
    act: update the password configuration in the provider charm.
    assert: secret content in the relation data should be updated.
    """
    peer_relation = PeerRelation(endpoint="smtp-peers")
    relation = Relation(endpoint="smtp", remote_app_name="smtp-requirer")
    password = secrets.token_hex()
    secret = Secret(
        tracked_content={"password": password},
        label="password-secret",
        owner="app",
    )
    state_in = State(
        leader=True,
        config={
            "host": "example.smtp",
            "port": 25,
            "user": "example_user",
            "auth_type": "plain",
            "password_secret": secret.id,
            "domain": "example.smtp",
        },
        relations=[peer_relation, relation],
        secrets=[secret],
    )
    state_out = context.run(context.on.config_changed(), state_in)

    relation_data = state_out.get_relation(relation.id).local_app_data
    assert relation_data is not None
    assert "password" not in relation_data
    assert secret.id == relation_data["password_id"]


def test_provider_charm_revoke_secret_on_broken(context: Context):
    """
    arrange: relate the smtp-consumer charm with a provider charm.
    act: remove the smtp relation.
    assert: secrets inside the smtp relation should be revoked.
    """
    peer_relation = PeerRelation(endpoint="smtp-peers")
    relation = Relation(endpoint="smtp", remote_app_name="smtp-requirer")
    password = secrets.token_hex()

    state_in = State(
        leader=True,
        config={
            "host": "example.smtp",
            "port": 25,
            "user": "example_user",
            "auth_type": "plain",
            "password": password,
            "domain": "example.smtp",
        },
        relations=[peer_relation, relation],
    )
    state_out = context.run(context.on.config_changed(), state_in)

    relation_data = state_out.get_relation(relation.id).local_app_data
    assert relation_data is not None
    password_id = relation_data["password_id"]
    secret = state_out.get_secret(id=password_id)

    # Verify secret is granted to the relation
    assert relation.id in secret.remote_grants

    # Trigger relation_broken - need to use the relation object from state_out
    relation_out = state_out.get_relation(relation.id)
    peer_out = state_out.get_relation(peer_relation.id)
    state_in2 = State(
        leader=True,
        config={
            "host": "example.smtp",
            "port": 25,
            "user": "example_user",
            "auth_type": "plain",
            "password": password,
            "domain": "example.smtp",
        },
        relations=[
            PeerRelation(
                endpoint="smtp-peers",
                id=peer_out.id,
                local_app_data=peer_out.local_app_data,
            ),
            relation_out,  # Keep the relation in state for relation_broken
        ],
        secrets=list(state_out.secrets),
    )
    state_out2 = context.run(context.on.relation_broken(relation_out), state_in2)

    # Verify secret is no longer granted to the relation
    secret2 = state_out2.get_secret(id=password_id)
    assert relation.id not in secret2.remote_grants


def test_provider_charm_update_secret_revision(context: Context):
    """
    arrange: relate the smtp-consumer charm with a provider charm.
    act: update the charm configuration in the provider charm.
    assert: secret revision in the relation data should remain unchanged.
    """
    peer_relation = PeerRelation(endpoint="smtp-peers")
    relation = Relation(endpoint="smtp", remote_app_name="smtp-requirer")
    password = secrets.token_hex()

    state_in = State(
        leader=True,
        config={
            "host": "example.smtp",
            "port": 25,
            "user": "example_user",
            "auth_type": "plain",
            "password": password,
            "domain": "example.smtp",
        },
        relations=[peer_relation, relation],
    )
    state_out = context.run(context.on.config_changed(), state_in)

    relation_data = state_out.get_relation(relation.id).local_app_data
    assert relation_data is not None
    password_id = relation_data["password_id"]
    secret = state_out.get_secret(id=password_id)
    initial_revision = secret._latest_revision  # pylint: disable=protected-access

    # Update config but not password - preserve peer data and secrets
    peer_out = state_out.get_relation(peer_relation.id)
    state_in2 = State(
        leader=True,
        config={
            "host": "example.smtp",
            "port": 25,
            "user": "example_user",
            "auth_type": "plain",
            "password": password,
            "domain": "smtp.example",
        },
        relations=[
            PeerRelation(
                endpoint="smtp-peers",
                local_app_data=peer_out.local_app_data,
            ),
            relation,
        ],
        secrets=list(state_out.secrets),
    )
    state_out2 = context.run(context.on.config_changed(), state_in2)
    secret2 = state_out2.get_secret(id=password_id)
    assert secret2._latest_revision == initial_revision  # pylint: disable=protected-access


def test_smtp_sender_when_misconfigured_then_charm_reaches_blocked_status(context: Context):
    """
    arrange: set up a charm with smtp_sender with invalid smtp_sender configuration.
    act: None
    assert: the charm reaches BlockedStatus.
    """
    state_in = State(
        leader=True,
        config=cast(
            dict[str, str | int | float | bool],
            {
                **MINIMAL_CHARM_CONFIG,
                "smtp_sender": "not-an-email",
            },
        ),
    )
    state_out = context.run(context.on.config_changed(), state_in)
    assert state_out.unit_status.name == ops.BlockedStatus().name


def test_smtp_sender_when_configured_then_charm_reaches_active_status(context: Context):
    """
    arrange: set up a charm with valid smtp_sender and minimal config.
    act: emit config_changed.
    assert: the charm reaches ActiveStatus.
    """
    state_in = State(
        config=cast(
            dict[str, str | int | float | bool],
            {
                **MINIMAL_CHARM_CONFIG,
                "smtp_sender": "no-reply@example.com",
            },
        )
    )
    state_out = context.run(context.on.config_changed(), state_in)
    assert state_out.unit_status == ops.ActiveStatus()


def test_recipients_when_misconfigured_then_charm_reaches_blocked_status(context: Context):
    """
    arrange: set up a charm with recipients containing an invalid email.
    act: none
    assert: the charm reaches BlockedStatus.
    """
    state_in = State(
        leader=True,
        config=cast(
            dict[str, str | int | float | bool],
            {
                **MINIMAL_CHARM_CONFIG,
                "recipients": "a@x.com,not-an-email",
            },
        ),
    )
    state_out = context.run(context.on.config_changed(), state_in)
    assert state_out.unit_status.name == ops.BlockedStatus().name


def test_recipients_when_configured_then_charm_reaches_active_status(context: Context):
    """
    arrange: set up a charm with valid recipients and minimal config.
    act: emit config_changed.
    assert: the charm reaches ActiveStatus.
    """
    state_in = State(
        config=cast(
            dict[str, str | int | float | bool],
            {
                **MINIMAL_CHARM_CONFIG,
                "recipients": "a@x.com,b@y.com",
            },
        )
    )
    state_out = context.run(context.on.config_changed(), state_in)
    assert state_out.unit_status == ops.ActiveStatus()


def test_legacy_relation_joined_when_sender_or_recipients_configured_then_populates(
    context: Context,
):
    """
    arrange: set up a charm with valid smtp_sender and recipients.
    act: trigger config_changed with smtp-legacy relation present.
    assert: relation data includes smtp_sender and recipients as JSON list string.
    """
    peer_relation = PeerRelation(endpoint="smtp-peers")
    relation = Relation(endpoint="smtp-legacy", remote_app_name="example")
    state_in = State(
        leader=True,
        config=cast(
            dict[str, str | int | float | bool],
            {**MINIMAL_CHARM_CONFIG_WITH_PASSWORD, **MINIMAL_CHARM_CONFIG_WITH_EMAILS},
        ),
        relations=[peer_relation, relation],
    )
    state_out = context.run(context.on.config_changed(), state_in)
    data = state_out.get_relation(relation.id).local_app_data
    assert data is not None

    assert data["smtp_sender"] == "no-reply@example.com"
    assert json.loads(str(data["recipients"])) == ["a@x.com", "b@y.com"]


def test_legacy_relation_joined_when_sender_or_recipients_unset_then_does_not_publish(
    context: Context,
):
    """
    arrange: charm with minimal config only.
    act: trigger config_changed with smtp-legacy relation present.
    assert: smtp_sender and recipients keys are not present.
    """
    peer_relation = PeerRelation(endpoint="smtp-peers")
    relation = Relation(endpoint="smtp-legacy", remote_app_name="example")
    state_in = State(
        leader=True,
        config=cast(dict[str, str | int | float | bool], MINIMAL_CHARM_CONFIG_WITH_PASSWORD),
        relations=[peer_relation, relation],
    )
    state_out = context.run(context.on.config_changed(), state_in)
    data = state_out.get_relation(relation.id).local_app_data
    assert data is not None

    assert "smtp_sender" not in data
    assert "recipients" not in data
