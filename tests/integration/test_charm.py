# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""SMTP Integrator charm integration tests."""

import json

import jubilant
import pytest

from tests.integration.helper import wait_for_provider_app_data


@pytest.mark.abort_on_fail
def test_active(juju: jubilant.Juju, app: str):
    """
    arrange: deploy the charm.
    act: configure the charm.
    assert: the charm reaches active status.
    """
    juju.config(app, {"host": "smtp.example"})
    juju.wait(jubilant.all_active)
    status = juju.status()
    assert status.apps[app].units[f"{app}/0"].is_active


@pytest.mark.abort_on_fail
def test_relation(
    juju: jubilant.Juju,
    app: str,
    any_charm: str,
    juju_version: str,
):
    """
    arrange: deploy the charm.
    act: integrate the charm through the smtp relation and configure it.
    assert: the charm reaches active status and publishes sender/recipients via relation data.
    """
    if int(juju_version.split(".")[0]) == 2:
        pytest.skip("skip smtp relation tests on juju 2")

    juju.integrate(f"{any_charm}:smtp", f"{app}:smtp")

    juju.config(
        app,
        {
            "host": "smtp.example",
            "smtp_sender": "no-reply@example.com",
            "recipients": "a@x.com,b@y.com",
        },
    )
    juju.wait(lambda status: jubilant.all_active(status, app, any_charm))
    status = juju.status()
    assert status.apps[app].units[f"{app}/0"].is_active

    data = wait_for_provider_app_data(
        juju=juju,
        endpoint="smtp",
        provider_app_name=app,
    )

    assert data["smtp_sender"] == "no-reply@example.com"
    assert json.loads(data["recipients"]) == ["a@x.com", "b@y.com"]


@pytest.mark.abort_on_fail
def test_legacy_relation(juju: jubilant.Juju, app: str, any_charm: str):
    """
    arrange: deploy the charm.
    act: integrate the charm through the smtp-legacy relation and configure it.
    assert: the charm reaches active status and publishes sender/recipients via relation data.
    """
    juju.integrate(f"{any_charm}:smtp-legacy", f"{app}:smtp-legacy")

    juju.config(
        app,
        {
            "host": "smtp.example",
            "smtp_sender": "no-reply@example.com",
            "recipients": "a@x.com,b@y.com",
        },
    )

    juju.wait(lambda status: jubilant.all_active(status, app, any_charm))
    status = juju.status()
    assert status.apps[app].units[f"{app}/0"].is_active

    data = wait_for_provider_app_data(
        juju=juju,
        endpoint="smtp-legacy",
        provider_app_name=app,
    )
    assert data["smtp_sender"] == "no-reply@example.com"
    assert json.loads(data["recipients"]) == ["a@x.com", "b@y.com"]
