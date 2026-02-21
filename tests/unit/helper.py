# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Helper methods for unit tests."""

import re


class RegexMatcher:
    """Regex matcher for unittest mocks."""

    def __init__(self, pattern):
        """Initialize with the regex pattern.

        Args:
            pattern: Regular expression pattern.
        """
        self.pattern = re.compile(pattern)

    def __eq__(self, other):
        """Compare the str argument against the regex.

        Args:
            other: String to match against.

        Returns:
            bool: True if pattern matches.
        """
        return bool(self.pattern.search(other))

    def __repr__(self):
        """Representation of the matcher.

        Returns:
            str: String representation.
        """
        return f"<RegexMatcher {self.pattern.pattern!r}>"
