#!/usr/bin/env python3
# Copyright 2023 Canonical Ltd.
# See LICENSE file for licensing details.

"""SMTP Integrator charm integration tests."""

import ops
import pytest
from pytest_operator.plugin import OpsTest


@pytest.mark.asyncio
@pytest.mark.abort_on_fail
async def test_active(ops_test: OpsTest, app: ops.Application):
    """Check that the charm is active.

    Assume that the charm has already been built and is running.
    """
    await app.set_config({"host": "smtp.example"})  # type: ignore[attr-defined]
    status_name = ops.ActiveStatus.name  # type: ignore[has-type]
    assert ops_test.model
    await ops_test.model.wait_for_idle(status=status_name, raise_on_error=True)
    assert app.units[0].workload_status == status_name  # type: ignore


@pytest.mark.asyncio
@pytest.mark.abort_on_fail
async def test_relation(ops_test: OpsTest, app: ops.Application, any_charm: ops.Application):
    """Check that the charm is active once related to another charm.

    Assume that the charm has already been built and is running.
    """
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
    """Check that the charm is active once related to another charm.

    Assume that the charm has already been built and is running.
    """
    assert ops_test.model
    relation_name = f"{app.name}:smtp-legacy"
    await ops_test.model.add_relation(f"{any_charm.name}:smtp-legacy", relation_name)
    await app.set_config({"host": "smtp.example"})  # type: ignore[attr-defined]
    status_name = ops.ActiveStatus.name  # type: ignore[has-type]
    await ops_test.model.wait_for_idle(status=status_name, raise_on_error=True)
    assert app.units[0].workload_status == status_name  # type: ignore
