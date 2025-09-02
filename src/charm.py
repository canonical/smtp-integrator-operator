#!/usr/bin/env python3

# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""SMTP Integrator Charm service."""

import logging
import typing

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

    def _on_relation_created(self, event: ops.RelationCreatedEvent) -> None:
        """Handle a change to the smtp relation.

        Args:
            event: relation created event.
        """
        if not self.model.unit.is_leader():
            return
        if self._has_secrets():
            secret = self._store_password_as_secret()
            secret.grant(event.relation)
        self._update_smtp_relation(event.relation)

    def _on_legacy_relation_created(self, event: ops.RelationCreatedEvent) -> None:
        """Handle a change to the smtp-legacy relation.

        Args:
            event: relation created event.
        """
        if not self.model.unit.is_leader():
            return
        self._update_smtp_legacy_relation(event.relation)

    def _on_config_changed(self, _) -> None:
        """Handle changes in configuration."""
        self.unit.status = ops.MaintenanceStatus("Configuring charm")
        if self._has_secrets():
            self._store_password_as_secret()
        self._update_relations()
        self.unit.status = ops.ActiveStatus()

    def _store_password_as_secret(self) -> ops.Secret:
        """Store the SMTP password as a secret.

        Returns:
            the secret id.
        """
        peer_relation = self.model.get_relation("smtp-peers")
        assert peer_relation  # nosec
        secret = None
        if secret_id := peer_relation.data[self.app].get("secret-id"):
            try:
                secret = self.model.get_secret(id=secret_id)
            except ops.SecretNotFoundError as exc:
                logger.exception("Failed to get secret id %s: %s", secret_id, str(exc))
                del peer_relation.data[self.app][secret_id]
        if not secret:
            try:
                secret = self.model.get_secret(label=smtp.PASSWORD_SECRET_LABEL)
            except ops.SecretNotFoundError:
                # https://github.com/canonical/operator/issues/2025
                secret = self.app.add_secret(
                    {"placeholder": "placeholder"}, label=smtp.PASSWORD_SECRET_LABEL
                )
        if self._charm_state.password:
            secret.set_content({"password": self._charm_state.password})
            peer_relation.data[self.app].update({"secret-id": typing.cast(str, secret.id)})
            return secret
        if secret_id:
            del peer_relation.data[self.app][secret_id]
        return secret

    def _update_relations(self) -> None:
        """Update all SMTP data for the existing relations."""
        if not self.model.unit.is_leader():
            return
        for relation in self.model.relations[self.smtp.relation_name]:
            self._update_smtp_relation(relation)
        for relation in self.model.relations[self.smtp_legacy.relation_name]:
            self._update_smtp_legacy_relation(relation)

    def _update_smtp_relation(self, relation: ops.Relation) -> None:
        """Update the smtp relation databag.

        Args:
            relation: the relation for which to update the databag.
        """
        if self._has_secrets():
            self.smtp.update_relation_data(relation, self._get_smtp_data())

    def _update_smtp_legacy_relation(self, relation: ops.Relation) -> None:
        """Update the smtp-legacy relation databag.

        Args:
            relation: the relation for which to update the databag.
        """
        self.smtp.update_relation_data(relation, self._get_legacy_smtp_data())

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
            skip_ssl_verify=self._charm_state.skip_ssl_verify,
        )

    def _get_smtp_data(self) -> smtp.SmtpRelationData:
        """Get relation data.

        Returns:
            SmtpRelationData containing the SMTP details.
        """
        peer_relation = self.model.get_relation("smtp-peers")
        assert peer_relation  # nosec
        password_id = peer_relation.data[self.app].get("secret-id")
        return smtp.SmtpRelationData(
            host=self._charm_state.host,
            port=self._charm_state.port,
            user=self._charm_state.user,
            password_id=password_id,
            auth_type=self._charm_state.auth_type,
            transport_security=self._charm_state.transport_security,
            domain=self._charm_state.domain,
            skip_ssl_verify=self._charm_state.skip_ssl_verify,
        )

    def _has_secrets(self) -> bool:
        """Check if current Juju version supports secrets.

        Returns:
            If secrets are supported or not.
        """
        juju_version = ops.JujuVersion.from_environ()
        return juju_version.has_secrets


if __name__ == "__main__":  # pragma: nocover
    ops.main.main(SmtpIntegratorOperatorCharm)
