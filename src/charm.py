#!/usr/bin/env python3

# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""SMTP Integrator Charm service."""

import itertools
import logging
import typing

import ops
import pydantic
from charms.smtp_integrator.v0 import smtp

logger = logging.getLogger(__name__)

PEER_RELATION_NAME = "smtp-peers"
VALID_LOG_LEVELS = ["info", "debug", "warning", "error", "critical"]


class CharmConfigInvalidError(Exception):
    """Exception raised when a charm configuration is found to be invalid.

    Attributes:
        msg (str): Explanation of the error.
    """

    def __init__(self, msg: str):
        """Initialize a new instance of the CharmConfigInvalidError exception.

        Args:
            msg (str): Explanation of the error.
        """
        self.msg = msg


class NotReadyError(Exception):
    """Exception raised when a charm is not ready yet."""


class SmtpIntegratorOperatorCharm(ops.CharmBase):
    """Charm the service."""

    def __init__(self, *args):
        """Construct.

        Args:
            args: Arguments passed to the CharmBase parent constructor.
        """
        super().__init__(*args)

        self.smtp = smtp.SmtpProvides(self)
        self.smtp_legacy = smtp.SmtpProvides(self, relation_name=smtp.LEGACY_RELATION_NAME)

        peer_events = self.on[PEER_RELATION_NAME]
        self.framework.observe(peer_events.relation_created, self._reconcile_event)
        self.framework.observe(peer_events.relation_changed, self._reconcile_event)

        legacy_events = self.on[smtp.LEGACY_RELATION_NAME].relation_created
        self.framework.observe(legacy_events, self._reconcile_event)

        smtp_events = self.on[smtp.DEFAULT_RELATION_NAME]
        self.framework.observe(smtp_events.relation_created, self._reconcile_event)
        self.framework.observe(smtp_events.relation_broken, self._on_relation_broken)

        self.framework.observe(self.on.config_changed, self._reconcile_event)

    def _reconcile_event(self, _: ops.EventBase) -> None:
        """Handle events that requires the reconciliation."""
        try:
            self._reconcile()
            self.unit.status = ops.ActiveStatus()
        except CharmConfigInvalidError as exc:
            self.unit.status = ops.BlockedStatus(str(exc))
        except NotReadyError as exc:
            self.unit.status = ops.WaitingStatus(str(exc))

    def _reconcile(self) -> None:
        """Reconcile the SMTP integrator."""
        if not self.unit.is_leader():
            return
        # sanity test for the charm configuration
        self._generate_smtp_data()

        self._reconcile_smtp_legacy()
        self._reconcile_smtp()

    def _reconcile_smtp_legacy(self) -> None:
        """Reconcile smtp_legacy relations."""
        for relation in self.model.relations[self.smtp_legacy.relation_name]:
            new_data = self._generate_smtp_data()
            new_data.password_id = None
            self.smtp_legacy.update_relation_data(relation, new_data)

    def _reconcile_smtp(self):
        """Reconcile smtp relations."""
        for relation in self.model.relations[self.smtp.relation_name]:
            if not self._has_secrets():
                raise CharmConfigInvalidError("smtp relation is not supported in juju < 3.0.3")
            new_data = self._generate_smtp_data()
            secret = self._get_peer_secret()
            if new_data.password_id:
                secret.grant(relation)
            if not new_data.password_id and secret is not None:
                secret.revoke(relation=relation)
            self.smtp.update_relation_data(relation, new_data)

    def _generate_smtp_data(self) -> smtp.SmtpRelationData:
        """Get relation data.

        Returns:
            SmtpRelationData containing the SMTP details.
        """
        password = typing.cast(typing.Optional[str], self.config.get("password"))
        if password and self._has_secrets():
            password_id = self._ensure_peer_secret(content={"password": password}).id
        else:
            password_id = None
        try:
            return smtp.SmtpRelationData(
                host=self.config.get("host"),
                port=self.config.get("port"),
                user=self.config.get("user"),
                password_id=password_id,
                password=password,
                auth_type=self.config.get("auth_type"),
                transport_security=self.config.get("transport_security"),
                domain=self.config.get("domain"),
                skip_ssl_verify=self.config.get("skip_ssl_verify"),
            )
        except pydantic.ValidationError as exc:
            error_fields = set(
                itertools.chain.from_iterable(error["loc"] for error in exc.errors())
            )
            error_field_str = " ".join(str(f) for f in error_fields)
            raise CharmConfigInvalidError(f"invalid configuration: {error_field_str}") from exc

    def _on_relation_broken(self, event: ops.RelationBrokenEvent) -> None:
        """Handle relation-broken events.

        Args:
            event: the relation broken event.
        """
        if not self.unit.is_leader():
            return
        secret = self._get_peer_secret()
        if secret:
            secret.revoke(event.relation)

    def _get_peer_data(self) -> ops.RelationDataContent:
        """Get peer relation data.

        Returns:
            Peer relation data.
        """
        peer_relation = self.model.get_relation(PEER_RELATION_NAME)
        if not peer_relation:
            raise NotReadyError("waiting for peer relation")
        return peer_relation.data[self.app]

    def _get_peer_secret(self) -> typing.Optional[ops.Secret]:
        """Get the secret stored inside the peer relation.

        Returns:
            Secret stored inside the peer relation.
        """
        secret_id = self._get_peer_data().get("secret-id")
        if not secret_id:
            return None
        return self.model.get_secret(id=secret_id)

    def _ensure_peer_secret(self, content: dict) -> ops.Secret:
        """Create a secret inside the peer relation, if the secret exists, update it.

        Args:
            content: create or update the secret with content
        """
        secret = self._get_peer_secret()
        if secret is None:
            secret = self.app.add_secret(content=content)
        self._get_peer_data()["secret-id"] = typing.cast(str, secret.id)
        if dict(secret.get_content(refresh=True)) != content:
            secret.set_content(content)
        return secret

    def _has_secrets(self) -> bool:
        """Check if current Juju version supports secrets.

        Returns:
            If secrets are supported or not.
        """
        juju_version = ops.JujuVersion.from_environ()
        return juju_version.has_secrets


if __name__ == "__main__":  # pragma: nocover
    ops.main.main(SmtpIntegratorOperatorCharm)
