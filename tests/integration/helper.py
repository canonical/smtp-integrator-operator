#!/usr/bin/env python3
# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""Integration test helpers."""

import asyncio
import json
from typing import Any, Dict

from pytest_operator.plugin import OpsTest


async def get_provider_app_databag_from_any_charm(
    ops_test: OpsTest, endpoint: str, provider_app_name: str
) -> Dict[str, Any]:
    """Read provider application databag as seen from any/0 via juju show-unit.

    Args:
        ops_test: pytest-operator fixture.
        endpoint: the endpoint name.
        provider_app_name: the provider application name.

    Returns:
        dict: the databag.

    Raises:
        AssertionError: if the databag is not found.
    """
    unit_name = "any/0"
    _, raw, _ = await ops_test.juju("show-unit", unit_name, "--format", "json")
    payload = json.loads(raw)[unit_name]

    for rel in payload.get("relation-info", []):
        if rel.get("endpoint") != endpoint:
            continue
        if rel.get("related-endpoint") != f"{provider_app_name}:{endpoint}":
            continue
        return rel.get("application-data", {})

    raise AssertionError(
        f"Did not find relation data for endpoint={endpoint} with provider app={provider_app_name}"
    )


async def wait_for_provider_app_data(
    ops_test: OpsTest,
    endpoint: str,
    provider_app_name: str,
    timeout: int = 120,
):
    """
    Wait until the provider application publishes relation data for an endpoint.

    This function polls the provider application's relation databag until it
    becomes available or a timeout is reached.

    Args:
        ops_test: The pytest-operator fixture.
        endpoint: The relation endpoint name.
        provider_app_name: The provider application name.
        timeout: Maximum time to wait (in seconds).

    Returns:
        A dictionary containing the provider application's relation databag.

    Raises:
        AssertionError: If the relation data does not appear within the timeout.
        last_error: Stores the last AssertionError raised while polling, so it can be
            re-raised on timeout to preserve the most relevant failure message.
    """
    deadline = asyncio.get_running_loop().time() + timeout
    last_error = None

    while asyncio.get_running_loop().time() < deadline:
        try:
            data = await get_provider_app_databag_from_any_charm(
                ops_test=ops_test,
                endpoint=endpoint,
                provider_app_name=provider_app_name,
            )
            if data:
                return data
        except AssertionError as e:
            last_error = e

        await asyncio.sleep(2)

    if last_error:
        raise last_error
    raise AssertionError(
        f"Timed out waiting for relation data: provider={provider_app_name}, endpoint={endpoint}"
    )
