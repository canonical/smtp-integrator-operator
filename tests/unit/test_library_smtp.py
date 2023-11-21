# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

"""SMTP library unit tests"""
import ops
import pytest
from charms.smtp_integrator.v0 import smtp
from ops.testing import Harness

REQUIRER_METADATA = """
name: smtp-consumer
requires:
  smtp:
    interface: smtp
  smtp-legacy:
    interface: smtp
"""

PROVIDER_METADATA = """
name: smtp-producer
provides:
  smtp:
    interface: smtp
  smtp-legacy:
    interface: smtp
"""


class SmtpRequirerCharm(ops.CharmBase):
    """Class for requirer charm testing."""

    def __init__(self, *args):
        """Init method for the class.

        Args:
            args: Variable list of positional arguments passed to the parent constructor.
        """
        super().__init__(*args)
        self.smtp = smtp.SmtpRequires(self)
        self.smtp_legacy = smtp.SmtpRequires(self, relation_name=smtp.LEGACY_RELATION_NAME)
        self.events = []
        self.framework.observe(self.smtp.on.smtp_data_available, self._record_event)
        self.framework.observe(self.smtp_legacy.on.smtp_data_available, self._record_event)

    def _record_event(self, event: ops.EventBase) -> None:
        """Record emitted event in the event list.

        Args:
            event: event.
        """
        self.events.append(event)


class SmtpProviderCharm(ops.CharmBase):
    """Class for provider charm testing."""

    def __init__(self, *args):
        """Init method for the class.

        Args:
            args: Variable list of positional arguments passed to the parent constructor.
        """
        super().__init__(*args)
        self.smtp = smtp.SmtpProvides(self)
        self.smtp_legacy = smtp.SmtpProvides(self, relation_name=smtp.LEGACY_RELATION_NAME)
        self.events = []
        self.framework.observe(self.on.smtp_relation_changed, self._record_event)
        self.framework.observe(self.on.smtp_legacy_relation_changed, self._record_event)

    def _record_event(self, event: ops.EventBase) -> None:
        """Record emitted event in the event list.

        Args:
            event: event.
        """
        self.events.append(event)


def test_smtp_provider_charm_realtions():
    """
    arrange: instantiate a SmtpProviderCharm and add a relation.
    act: obtain the relations.
    assert: the relations retrieved match the existing relations.
    """
    harness = Harness(SmtpProviderCharm, meta=PROVIDER_METADATA)
    harness.begin()
    harness.set_leader(True)
    harness.add_relation("smtp-legacy", "smtp-provider")
    assert len(harness.charm.smtp_legacy.relations) == 1
    assert len(harness.charm.smtp.relations) == 0


def test_smtp_provider_update_relation_data():
    """
    arrange: instantiate a SmtpProviderCharm object and add a relation.
    act: update the relation data.
    assert: the relation data is updated.
    """
    harness = Harness(SmtpProviderCharm, meta=PROVIDER_METADATA)
    harness.begin()
    harness.set_leader(True)
    harness.add_relation("smtp-legacy", "smtp-provider")
    relation = harness.model.get_relation("smtp-legacy")
    smtp_data = smtp.SmtpRelationData(
        host="example.smtp",
        port=25,
        auth_type="plain",
        transport_security="tls",
    )
    harness.charm.smtp_legacy.update_relation_data(relation, smtp_data)
    data = relation.data[harness.model.app]
    assert data["host"] == smtp_data.host
    assert data["port"] == str(smtp_data.port)
    assert data["auth_type"] == smtp_data.auth_type
    assert data["transport_security"] == smtp_data.transport_security


def test_smtp_relation_data_to_relation_data():
    """
    arrange: instantiate a SmtpRelationData object.
    act: obtain the relation representation.
    assert: the relation representation is correct.
    """
    smtp_data = smtp.SmtpRelationData(
        host="example.smtp",
        port=25,
        user="example_user",
        password="somepassword",  # nosec
        password_id="someid",
        auth_type="plain",
        transport_security="tls",
        domain="domain",
    )
    relation_data = smtp_data.to_relation_data()
    expected_relation_data = {
        "host": "example.smtp",
        "port": "25",
        "user": "example_user",
        "password": "somepassword",  # nosec
        "password_id": "someid",
        "auth_type": "plain",
        "transport_security": "tls",
        "domain": "domain",
    }
    assert relation_data == expected_relation_data


def test_legacy_requirer_charm_does_not_emit_event_id_when_no_data():
    """
    arrange: set up a charm with no relation data to be populated.
    act: trigger a relation changed event.
    assert: no events are emitted.
    """
    harness = Harness(SmtpRequirerCharm, meta=REQUIRER_METADATA)
    harness.begin()
    harness.set_leader(True)
    harness.add_relation("smtp-legacy", "smtp-provider")
    relation = harness.charm.framework.model.get_relation("smtp-legacy", 0)
    harness.charm.on.smtp_legacy_relation_changed.emit(relation)
    assert len(harness.charm.events) == 0


def test_requirer_charm_does_not_emit_event_id_when_no_data():
    """
    arrange: set up a charm with no relation data to be populated.
    act: trigger a relation changed event.
    assert: no events are emitted.
    """
    harness = Harness(SmtpRequirerCharm, meta=REQUIRER_METADATA)
    harness.begin()
    harness.set_leader(True)
    harness.add_relation("smtp", "smtp-provider")
    relation = harness.charm.framework.model.get_relation("smtp", 0)
    harness.charm.on.smtp_legacy_relation_changed.emit(relation)
    assert len(harness.charm.events) == 0


@pytest.mark.parametrize("is_leader", [True, False])
def test_legacy_requirer_charm_with_valid_relation_data_emits_event(is_leader):
    """
    arrange: set up a charm.
    act: trigger a relation changed event with valid data.
    assert: a event containing the relation data is emitted.
    """
    relation_data = {
        "host": "example.smtp",
        "port": "25",
        "user": "example_user",
        "password": "somepassword",  # nosec
        "auth_type": "plain",
        "transport_security": "tls",
        "domain": "domain",
    }

    harness = Harness(SmtpRequirerCharm, meta=REQUIRER_METADATA)
    harness.begin()
    harness.set_leader(is_leader)
    harness.add_relation("smtp-legacy", "smtp-provider", app_data=relation_data)

    assert len(harness.charm.events) == 1
    assert harness.charm.events[0].host == relation_data["host"]
    assert harness.charm.events[0].port == int(relation_data["port"])
    assert harness.charm.events[0].user == relation_data["user"]
    assert harness.charm.events[0].password == relation_data["password"]
    assert harness.charm.events[0].auth_type == relation_data["auth_type"]
    assert harness.charm.events[0].transport_security == relation_data["transport_security"]
    assert harness.charm.events[0].domain == relation_data["domain"]

    retrieved_relation_data = harness.charm.smtp_legacy.get_relation_data()
    assert retrieved_relation_data.host == relation_data["host"]
    assert retrieved_relation_data.port == int(relation_data["port"])
    assert retrieved_relation_data.user == relation_data["user"]
    assert retrieved_relation_data.password == relation_data["password"]
    assert retrieved_relation_data.auth_type == relation_data["auth_type"]
    assert retrieved_relation_data.transport_security == relation_data["transport_security"]
    assert retrieved_relation_data.domain == relation_data["domain"]


@pytest.mark.parametrize("is_leader", [True, False])
def test_requirer_charm_with_valid_relation_data_emits_event(is_leader):
    """
    arrange: set up a charm.
    act: trigger a relation changed event with valid data.
    assert: a event containing the relation data is emitted.
    """
    relation_data = {
        "host": "example.smtp",
        "port": "25",
        "user": "example_user",
        "password_id": "someid",
        "auth_type": "plain",
        "transport_security": "tls",
        "domain": "domain",
    }

    harness = Harness(SmtpRequirerCharm, meta=REQUIRER_METADATA)
    harness.begin()
    harness.set_leader(is_leader)
    harness.add_relation("smtp", "smtp-provider", app_data=relation_data)

    assert len(harness.charm.events) == 1
    assert harness.charm.events[0].host == relation_data["host"]
    assert harness.charm.events[0].port == int(relation_data["port"])
    assert harness.charm.events[0].user == relation_data["user"]
    assert harness.charm.events[0].password_id == relation_data["password_id"]
    assert harness.charm.events[0].auth_type == relation_data["auth_type"]
    assert harness.charm.events[0].transport_security == relation_data["transport_security"]
    assert harness.charm.events[0].domain == relation_data["domain"]


@pytest.mark.parametrize("is_leader", [True, False])
def test_requirer_charm_with_invalid_relation_data_doesnt_emit_event(is_leader):
    """
    arrange: set up a charm.
    act: trigger a relation changed event with invalid data.
    assert: an event containing the relation data is not emitted.
    """
    relation_data = {
        "port": "25",
        "user": "example_user",
        "password": "somepassword",  # nosec
        "auth_type": "plain",
        "transport_security": "tls",
        "domain": "domain",
    }

    harness = Harness(SmtpRequirerCharm, meta=REQUIRER_METADATA)
    harness.begin()
    harness.set_leader(is_leader)
    harness.add_relation("smtp-legacy", "smtp-provider", app_data=relation_data)

    assert len(harness.charm.events) == 0
