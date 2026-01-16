#!/usr/bin/env python3
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""SMTP Integrator charm integration tests."""

import json

import ops
import pytest
from pytest_operator.plugin import OpsTest

from tests.integration.helper import get_provider_app_databag_from_any_charm


@pytest.mark.asyncio
@pytest.mark.abort_on_fail
async def test_active(ops_test: OpsTest, app: ops.Application):
    """
    arrange: deploy the charm.
    act: configure the charm.
    assert: the charm reaches active status.
    """
    await app.set_config({"host": "smtp.example"})  # type: ignore[attr-defined]
    status_name = ops.ActiveStatus.name  # type: ignore[has-type]
    assert ops_test.model
    await ops_test.model.wait_for_idle(status=status_name, raise_on_error=True)
    assert app.units[0].workload_status == status_name  # type: ignore


@pytest.mark.asyncio
@pytest.mark.abort_on_fail
async def test_relation(
    ops_test: OpsTest,
    app: ops.Application,
    any_charm: ops.Application,
    juju_version: str,
):
    """
    arrange: deploy the charm.
    act: integrate the charm through the smtp relation and configure it.
    assert: the charm reaches active status and publishes sender/recipients via relation data.
    """
    if int(juju_version.split(".")[0]) == 2:
        pytest.skip("skip smtp relation tests on juju 2")

    assert ops_test.model
    await ops_test.model.add_relation(f"{any_charm.name}:smtp", f"{app.name}:smtp")

    await app.set_config(  # type: ignore[attr-defined]
        {
            "host": "smtp.example",
            "smtp_sender": "no-reply@example.com",
            "recipients": "a@x.com,b@y.com",
        }
    )
    status_name = ops.ActiveStatus.name  # type: ignore[has-type]
    await ops_test.model.wait_for_idle(status=status_name, raise_on_error=True)
    assert app.units[0].workload_status == status_name  # type: ignore

    data = await get_provider_app_databag_from_any_charm(
        ops_test=ops_test,
        endpoint="smtp",
        provider_app_name=app.name,
    )
    assert data["smtp_sender"] == "no-reply@example.com"
    assert json.loads(data["recipients"]) == ["a@x.com", "b@y.com"]


@pytest.mark.asyncio
@pytest.mark.abort_on_fail
async def test_legacy_relation(
    ops_test: OpsTest, app: ops.Application, any_charm: ops.Application
):
    """
    arrange: deploy the charm.
    act: integrate the charm through the smtp-legacy relation and configure it.
    assert: the charm reaches active status and publishes sender/recipients via relation data.
    """
    assert ops_test.model
    await ops_test.model.add_relation(f"{any_charm.name}:smtp-legacy", f"{app.name}:smtp-legacy")

    await app.set_config(  # type: ignore[attr-defined]
        {
            "host": "smtp.example",
            "smtp_sender": "no-reply@example.com",
            "recipients": "a@x.com,b@y.com",
        }
    )

    status_name = ops.ActiveStatus.name  # type: ignore[has-type]
    await ops_test.model.wait_for_idle(status=status_name, raise_on_error=True)
    assert app.units[0].workload_status == status_name  # type: ignore

    data = await get_provider_app_databag_from_any_charm(
        ops_test=ops_test,
        endpoint="smtp-legacy",
        provider_app_name=app.name,
    )
    assert data["smtp_sender"] == "no-reply@example.com"
    assert json.loads(data["recipients"]) == ["a@x.com", "b@y.com"]
