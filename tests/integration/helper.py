#!/usr/bin/env python3
# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""Integration test helpers."""

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
