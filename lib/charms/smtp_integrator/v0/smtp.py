#!/usr/bin/env python3

# Copyright 2023 Canonical Ltd.
# Licensed under the Apache2.0. See LICENSE file in charm source for details.

"""Library to manage the relation data for the SMTP Integrator charm.

This library contains the Requires and Provides classes for handling the relation
between an application and a charm providing the `smtp`relation.
It also contains a `SmtpRelationData` class to wrap the SMTP data that will
be shared via the relation.

### Requirer Charm

```python

from charms.mtp_integrator.v0 import SmtpDataAvailableEvent, SmtpRequires

class SmtpRequirerCharm(ops.CharmBase):
    def __init__(self, *args):
        super().__init__(*args)
        self.smtp = smtp.SmtpRequires(self)
        self.framework.observe(self.smtp.on.smtp_data_available, self._handler)
        ...

    def _handler(self, events: SmtpDataAvailableEvent) -> None:
        ...

```

As shown above, the library provides a custom event to handle the sceneario in
which new SMTP data has been added or updated.

### Provider Charm

Following the previous example, this is an example of the provider charm.

```python
from charms.smtp_integrator.v0 import SmtpDataAvailableEvent, SmtpRequires

class SmtpRequirerCharm(ops.CharmBase):
    def __init__(self, *args):
        super().__init__(*args)
        self.smtp = SmtpRequires(self)
        self.framework.observe(self.smtp.on.smtp_data_available, self._on_smtp_data_available)
        ...

    def _on_smtp_data_available(self, events: SmtpDataAvailableEvent) -> None:
        ...

    def __init__(self, *args):
        super().__init__(*args)
        self.smtp = SmtpProvides(self)

```
The SmtpProvides object wraps the list of relations into a `relations` property
and provides an `update_relation_data` method to update the relation data by passing
a `SmtpRelationData` data object.
"""

# The unique Charmhub library identifier, never change it
LIBID = "018a12e798714b69829be1e9a5c481a5"

# Increment this major API version when introducing breaking changes
LIBAPI = 0

# Increment this PATCH version before using `charmcraft publish-lib` or reset
# to 0 if you are raising the major API version
LIBPATCH = 1

# pylint: disable=wrong-import-position
from enum import Enum
from typing import Optional

import ops
from pydantic import BaseModel, Field

DEFAULT_RELATION_NAME = "smtp-legacy"


class TransportSecurity(str, Enum):
    """Represent the transport security values.

    Attrs:
        NONE: none
        STARTTLS: starttls
        TLS: tls
    """

    NONE = "none"
    STARTTLS = "starttls"
    TLS = "tls"


class AuthType(str, Enum):
    """Represent the auth type values.

    Attrs:
        NONE: none
        NOT_PROVIDED: not_provided
        PLAIN: plain
    """

    NONE = "none"
    NOT_PROVIDED = "not_provided"
    PLAIN = "plain"


class SmtpRelationData(BaseModel):
    """Represent the relation data.

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
    auth_type: AuthType
    transport_security: TransportSecurity
    domain: Optional[str]

    def to_relation_data(self) -> dict[str, str]:
        """Convert an instance of SmtpRelationData to the relation representation.

        Returns:
            Dict containing the representation.
        """
        result = {
            "host": str(self.host),
            "port": str(self.port),
            "auth_type": self.auth_type.value,
            "transport_security": self.transport_security.value,
        }
        if self.domain:
            result["domain"] = self.domain
        if self.user:
            result["user"] = self.user
        if self.password:
            result["password"] = self.password
        return result


class SmtpDataAvailableEvent(ops.RelationEvent):
    """Smtp event emitted when relation data has changed.

    Attrs:
        host: The hostname or IP address of the outgoing SMTP relay.
        port: The port of the outgoing SMTP relay.
        user: The SMTP AUTH user to use for the outgoing SMTP relay.
        password: The SMTP AUTH password to use for the outgoing SMTP relay.
        auth_type: The type used to authenticate with the SMTP relay.
        transport_security: The security protocol to use for the outgoing SMTP relay.
        domain: The domain used by the sent emails from SMTP relay.
    """

    @property
    def host(self) -> str:
        """Fetch the SMTP host from the relation."""
        assert self.relation.app
        return self.relation.data[self.relation.app].get("host")

    @property
    def port(self) -> int:
        """Fetch the SMTP port from the relation."""
        assert self.relation.app
        return int(self.relation.data[self.relation.app].get("port"))

    @property
    def user(self) -> str:
        """Fetch the SMTP user from the relation."""
        assert self.relation.app
        return self.relation.data[self.relation.app].get("user")

    @property
    def password(self) -> str:
        """Fetch the SMTP password from the relation."""
        assert self.relation.app
        return self.relation.data[self.relation.app].get("password")

    @property
    def auth_type(self) -> str:
        """Fetch the SMTP auth type from the relation."""
        assert self.relation.app
        return self.relation.data[self.relation.app].get("auth_type")

    @property
    def transport_security(self) -> str:
        """Fetch the SMTP transport security protocol from the relation."""
        assert self.relation.app
        return self.relation.data[self.relation.app].get("transport_security")

    @property
    def domain(self) -> str:
        """Fetch the SMTP domain from the relation."""
        assert self.relation.app
        return self.relation.data[self.relation.app].get("domain")


class SmtpRequiresEvents(ops.CharmEvents):
    """SMTP events.

    This class defines the events that a SMTP requirer can emit.

    Attrs:
        smtp_data_available: the SmtpDataAvailableEvent.
    """

    smtp_data_available = ops.EventSource(SmtpDataAvailableEvent)


class SmtpRequires(ops.Object):
    """Requirer side of the SMTP relation.

    Attrs:
        on: events the provider can emit.
    """

    on = SmtpRequiresEvents()

    def __init__(self, charm: ops.CharmBase, relation_name: str = DEFAULT_RELATION_NAME) -> None:
        """Construct.

        Args:
            charm: the provider charm.
            relation_name: the relation name.
        """
        super().__init__(charm, relation_name)
        self.charm = charm
        self.relation_name = relation_name
        self.framework.observe(charm.on[relation_name].relation_changed, self._on_relation_changed)

    def _on_relation_changed(self, event: ops.RelationChangedEvent) -> None:
        """Event emitted when the relation has changed.

        Args:
            event: event triggering this handler.
        """
        assert event.relation.app
        if event.relation.data[event.relation.app]:
            self.on.smtp_data_available.emit(event.relation, app=event.app, unit=event.unit)


class SmtpProvides(ops.Object):
    """Provider side of the SMTP relation.

    Attrs:
        relations: list of charm relations.
    """

    def __init__(self, charm: ops.CharmBase, relation_name: str = DEFAULT_RELATION_NAME) -> None:
        """Construct.

        Args:
            charm: the provider charm.
            relation_name: the relation name.
        """
        super().__init__(charm, relation_name)
        self.charm = charm
        self.relation_name = relation_name

    @property
    def relations(self) -> list[ops.Relation]:
        """The list of Relation instances associated with this relation_name.

        Returns:
            List of relations to this charm.
        """
        return list(self.model.relations[self.relation_name])

    def update_relation_data(self, relation: ops.Relation, smtp_data: SmtpRelationData) -> None:
        """Update the relation data.

        Args:
            relation: the relation for which to update the data.
            smtp_data: a SmtpRelationData instance wrapping the data to be updated.
        """
        relation.data[self.charm.model.app].update(smtp_data.to_relation_data())