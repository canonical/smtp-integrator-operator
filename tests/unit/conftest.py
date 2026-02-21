# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Fixtures for SMTP Integrator unit tests."""

import secrets

import pytest
from scenario import Context

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


@pytest.fixture(name="context")
def context_fixture():
    """Context fixture for SmtpIntegratorOperatorCharm.

    Returns:
        Context: Test context for the charm.
    """
    return Context(SmtpIntegratorOperatorCharm)
