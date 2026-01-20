# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""SMTP interface tests."""

import pytest
from interface_tester import InterfaceTester


# https://github.com/canonical/pytest-interface-tester/issues/27
@pytest.mark.skip
def test_smtp_v0_interface(interface_tester: InterfaceTester):
    """Test smtp interface.

    Args:
        interface_tester: interface tester.
    """
    interface_tester.configure(
        juju_version="3.4",
        interface_name="smtp",
        interface_version=0,
    )
    interface_tester.run()
