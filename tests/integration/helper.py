#!/usr/bin/env python3
# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""Integration test helpers."""

import json
import time
from typing import Any, Dict

import jubilant


def get_provider_app_databag_from_any_charm(
    juju: jubilant.Juju, endpoint: str, provider_app_name: str
) -> Dict[str, Any]:
    """Read provider application databag as seen from any/0 via juju show-unit.

    Args:
        juju: jubilant Juju instance.
        endpoint: the endpoint name.
        provider_app_name: the provider application name.

    Returns:
        dict: the databag.

    Raises:
        AssertionError: if the databag is not found.
    """
    unit_name = "any/0"
    raw = juju.cli("show-unit", unit_name, "--format", "json")
    payload = json.loads(raw)[unit_name]

    for rel in payload.get("relation-info", []):
        if rel.get("endpoint") != endpoint:
            continue
        related_units = rel.get("related-units", {}) or {}
        if not any(u.split("/")[0] == provider_app_name for u in related_units):
            continue

        return rel.get("application-data", {}) or {}

    raise AssertionError(
        f"Did not find relation data for endpoint={endpoint} with provider app={provider_app_name}"
    )


def wait_for_provider_app_data(
    juju: jubilant.Juju,
    endpoint: str,
    provider_app_name: str,
    timeout: int = 120,
):
    """
    Wait until the provider application publishes relation data for an endpoint.

    This function polls the provider application's relation databag until it
    becomes available or a timeout is reached.

    Args:
        juju: The jubilant Juju instance.
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
    deadline = time.time() + timeout
    last_error = None

    while time.time() < deadline:
        try:
            data = get_provider_app_databag_from_any_charm(
                juju=juju,
                endpoint=endpoint,
                provider_app_name=provider_app_name,
            )
            if data:
                return data
        except AssertionError as e:
            last_error = e

        time.sleep(2)

    if last_error:
        raise last_error
    raise AssertionError(
        f"Timed out waiting for relation data: provider={provider_app_name}, endpoint={endpoint}"
    )
