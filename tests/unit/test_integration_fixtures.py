# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""Tests for integration artifact selection."""

from unittest.mock import Mock

import pytest
from pytest import Config

from tests.integration.conftest import charm_file_fixture


@pytest.mark.parametrize("base", ["ubuntu@22.04", "ubuntu@24.04", "ubuntu@26.04"])
@pytest.mark.parametrize("machine,architecture", [("x86_64", "amd64"), ("aarch64", "arm64")])
def test_charm_file_matches_base_and_architecture(monkeypatch, base, machine, architecture):
    """
    arrange: provide artifacts for every supported base and architecture.
    act: select the artifact for the runner and requested base.
    assert: exactly the matching artifact is returned, regardless of input order.
    """
    charm_files = [
        f"./smtp-integrator_ubuntu@{version}-{arch}.charm"
        for version in ["22.04", "24.04", "26.04"]
        for arch in ["amd64", "arm64"]
    ]
    config = Mock(spec=Config)
    config.getoption.return_value = charm_files
    monkeypatch.setattr("tests.integration.conftest.platform.machine", lambda: machine)

    assert next(charm_file_fixture.__wrapped__(config, base)) == (
        f"./smtp-integrator_{base}-{architecture}.charm"
    )


@pytest.mark.parametrize(
    "charm_files",
    [
        [],
        ["./smtp-integrator_ubuntu@24.04-amd64.charm"],
        ["./smtp-integrator_ubuntu@22.04-arm64.charm"],
        [
            "./smtp-integrator_ubuntu@24.04-arm64.charm",
            "./other/smtp-integrator_ubuntu@24.04-arm64.charm",
        ],
    ],
)
def test_charm_file_rejects_missing_or_ambiguous_artifacts(monkeypatch, charm_files):
    """
    arrange: provide missing, incompatible, or duplicate artifacts for an ARM64 runner.
    act: select the artifact for Ubuntu 24.04.
    assert: selection fails explicitly instead of deploying an arbitrary artifact.
    """
    config = Mock(spec=Config)
    config.getoption.return_value = charm_files
    monkeypatch.setattr("tests.integration.conftest.platform.machine", lambda: "aarch64")

    with pytest.raises(ValueError, match="Expected one charm file"):
        next(charm_file_fixture.__wrapped__(config, "ubuntu@24.04"))


def test_charm_file_rejects_unsupported_architecture(monkeypatch):
    """
    arrange: run on an unsupported architecture.
    act: select a charm artifact.
    assert: selection fails with the unsupported architecture in the error.
    """
    config = Mock(spec=Config)
    config.getoption.return_value = []
    monkeypatch.setattr("tests.integration.conftest.platform.machine", lambda: "riscv64")

    with pytest.raises(ValueError, match="Unsupported runner architecture 'riscv64'"):
        next(charm_file_fixture.__wrapped__(config, "ubuntu@24.04"))
