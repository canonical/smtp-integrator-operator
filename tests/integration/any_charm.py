# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

# pylint: disable=import-error,consider-using-with,no-member

"""This code snippet is used to be loaded into any-charm which is used for integration tests."""
import smtp
from any_charm_base import AnyCharmBase


class AnyCharm(AnyCharmBase):  # pylint: disable=too-few-public-methods
    """Execute a simple charm workload to test the smtp relation.

    Attributes:
        smtp: The attribute that mimics a real SMTP relation.
    """

    def __init__(self, *args, **kwargs):
        """Init function for the class.

        Args:
            args: Variable list of positional arguments passed to the parent constructor.
            kwargs: Variable list of positional keyword arguments passed to the parent constructor.
        """
        super().__init__(*args, **kwargs)
        self.smtp = smtp.SmtpRequires(self)
        self.smtp_legacy = smtp.SmtpRequires(self, relation_name=smtp.LEGACY_RELATION_NAME)
