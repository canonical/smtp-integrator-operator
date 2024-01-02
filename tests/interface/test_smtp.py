# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

"""SMTP interface tests."""
from interface_tester import InterfaceTester


def test_smtp_v0_interface(interface_tester: InterfaceTester):
    """Test smtp interface.

    Args:
        interface_tester: interface tester.
    """
    interface_tester.configure(
        repo="https://github.com/canonical/charm-relation-interfaces",
        branch="main",
        juju_version="3.4",
        interface_name="smtp",
        interface_version=0,
    )
    interface_tester.run()
