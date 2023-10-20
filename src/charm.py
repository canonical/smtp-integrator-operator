#!/usr/bin/env python3

# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

"""SMTP Integrator Charm service."""

import logging

import ops
from charms.smtp_integrator.v0 import smtp

from charm_state import CharmConfigInvalidError, CharmState

logger = logging.getLogger(__name__)

VALID_LOG_LEVELS = ["info", "debug", "warning", "error", "critical"]


class SmtpIntegratorOperatorCharm(ops.CharmBase):
    """Charm the service."""

    def __init__(self, *args):
        """Construct.

        Args:
            args: Arguments passed to the CharmBase parent constructor.
        """
        super().__init__(*args)
        try:
            self._charm_state = CharmState.from_charm(charm=self)
        except CharmConfigInvalidError as exc:
            self.model.unit.status = ops.BlockedStatus(exc.msg)
            return
        self.smtp = smtp.SmtpProvides(self)
        self.smtp_legacy = smtp.SmtpProvides(self, relation_name=smtp.LEGACY_RELATION_NAME)
        self.framework.observe(
            self.on[smtp.LEGACY_RELATION_NAME].relation_created, self._on_legacy_relation_created
        )
        self.framework.observe(
            self.on[smtp.DEFAULT_RELATION_NAME].relation_created, self._on_relation_created
        )
        self.framework.observe(self.on.config_changed, self._on_config_changed)
        self.framework.observe(self.on.update_status, self._on_update_status)

    def _on_relation_created(self, event: ops.RelationCreatedEvent) -> None:
        """Handle a change to the smtp relation.

        Args:
            event: Relation created event.
        """
        if secret_id := self._charm_state.password_id:
            secret = self.model.get_secret(id=secret_id)
            secret.grant(event.relation)
        # A new charm will be instantiated hence, the information will be fetched again.
        # The relation databags are rewritten in case there are changes.
        self._update_relations()

    def _on_legacy_relation_created(self, _) -> None:
        """Handle a change to the smtp-legacy relation."""
        # A new charm will be instantiated hence, the information will be fetched again.
        # The relation databags are rewritten in case there are changes.
        self._update_relations()

    def _on_update_status(self, _) -> None:
        """Handle the update status event."""
        # A new charm will be instantiated hence, the information will be fetched again.
        # The relation databags are rewritten in case there are changes.
        self._update_relations()

    def _on_config_changed(self, _) -> None:
        """Handle changes in configuration."""
        self.unit.status = ops.MaintenanceStatus("Configuring charm")
        self._store_password_as_secret()
        self._update_relations()
        self.unit.status = ops.ActiveStatus()

    def _store_password_as_secret(self) -> None:
        """Store the SMTP password as a secret."""
        if self._charm_state.password:
            secret = self.app.add_secret({"password": self._charm_state.password})
            self._charm_state.password_id = secret.id

    def _update_relations(self) -> None:
        """Update all SMTP data for the existing relations."""
        if not self.model.unit.is_leader():
            return
        for relation in self.smtp.relations:
            self.smtp.update_relation_data(relation, self._get_smtp_data())
        for relation in self.smtp_legacy.relations:
            self.smtp_legacy.update_relation_data(relation, self._get_legacy_smtp_data())

    def _get_legacy_smtp_data(self) -> smtp.SmtpRelationData:
        """Get relation data.

        Returns:
            SmtpRelationData containing the SMTP details.
        """
        return smtp.SmtpRelationData(
            host=self._charm_state.host,
            port=self._charm_state.port,
            user=self._charm_state.user,
            password=self._charm_state.password,
            auth_type=self._charm_state.auth_type,
            transport_security=self._charm_state.transport_security,
            domain=self._charm_state.domain,
        )

    def _get_smtp_data(self) -> smtp.SmtpRelationData:
        """Get relation data.

        Returns:
            SmtpRelationData containing the SMTP details.
        """
        return smtp.SmtpRelationData(
            host=self._charm_state.host,
            port=self._charm_state.port,
            user=self._charm_state.user,
            password_id=self._charm_state.password_id,
            auth_type=self._charm_state.auth_type,
            transport_security=self._charm_state.transport_security,
            domain=self._charm_state.domain,
        )


if __name__ == "__main__":  # pragma: nocover
    ops.main.main(SmtpIntegratorOperatorCharm)
