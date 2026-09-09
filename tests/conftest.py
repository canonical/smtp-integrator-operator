# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Fixtures for charm tests."""


def pytest_addoption(parser):
    """Parse additional pytest options.

    Args:
        parser: Pytest parser.
    """
    # The charm is built for several bases, so the CI passes one --charm-file per
    # built charm and the integration tests pick the one matching --series.
    parser.addoption("--charm-file", action="append", default=[])
    parser.addoption("--series", action="store", default=None)
