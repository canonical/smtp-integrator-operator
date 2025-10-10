#!/usr/bin/env python3
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""SMTP Integrator charm integration tests."""

import ops
import pytest
from pytest_operator.plugin import OpsTest


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
    assert: the charm reaches active status.
    """
    if int(juju_version.split(".")[0]) == 2:
        pytest.skip("skip smtp relation tests on juju 2")
    assert ops_test.model
    relation_name = f"{app.name}:smtp"
    await ops_test.model.add_relation(f"{any_charm.name}:smtp", relation_name)
    await app.set_config({"host": "smtp.example"})  # type: ignore[attr-defined]
    status_name = ops.ActiveStatus.name  # type: ignore[has-type]
    await ops_test.model.wait_for_idle(status=status_name, raise_on_error=True)
    assert app.units[0].workload_status == status_name  # type: ignore


@pytest.mark.asyncio
@pytest.mark.abort_on_fail
async def test_legacy_relation(
    ops_test: OpsTest, app: ops.Application, any_charm: ops.Application
):
    """
    arrange: deploy the charm.
    act: integrate the charm through the smtp-legacy relation and configure it.
    assert: the charm reaches active status.
    """
    assert ops_test.model
    relation_name = f"{app.name}:smtp-legacy"
    await ops_test.model.add_relation(f"{any_charm.name}:smtp-legacy", relation_name)
    await app.set_config({"host": "smtp.example"})  # type: ignore[attr-defined]
    status_name = ops.ActiveStatus.name  # type: ignore[has-type]
    await ops_test.model.wait_for_idle(status=status_name, raise_on_error=True)
    assert app.units[0].workload_status == status_name  # type: ignore
