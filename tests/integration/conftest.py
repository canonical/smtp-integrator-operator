# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Fixtures for the SMTP Integrator charm integration tests."""

import json
from pathlib import Path

import pytest_asyncio
import yaml
from pytest import Config, fixture
from pytest_operator.plugin import OpsTest

# Ubuntu series the charm is built for, mapped to the Juju base they correspond to.
# Keep in sync with the platforms in charmcraft.yaml.
SERIES_TO_BASE = {
    "jammy": "ubuntu@22.04",
    "noble": "ubuntu@24.04",
    "resolute": "ubuntu@26.04",
}
DEFAULT_SERIES = "jammy"


@fixture(scope="module", name="app_name")
def app_name_fixture():
    """Provide app name from the metadata."""
    metadata = yaml.safe_load(Path("./metadata.yaml").read_text("utf-8"))
    yield metadata["name"]


@fixture(scope="module", name="base")
def base_fixture(pytestconfig: Config):
    """Provide the Juju base to deploy on, derived from the --series option.

    Raises:
        ValueError: if the requested series is not one the charm is built for.
    """
    series = pytestconfig.getoption("--series") or DEFAULT_SERIES
    if series not in SERIES_TO_BASE:
        raise ValueError(
            f"Unsupported series {series!r}, expected one of {sorted(SERIES_TO_BASE)}"
        )
    yield SERIES_TO_BASE[series]


@fixture(scope="module", name="charm_file")
def charm_file_fixture(pytestconfig: Config, base: str):
    """Provide the built charm file matching the base under test.

    Raises:
        ValueError: if no charm was built for the base under test.
    """
    charm_files = pytestconfig.getoption("--charm-file")
    # Multi-base builds name the artefacts after their base, for example
    # smtp-integrator_ubuntu@24.04-amd64.charm.
    channel = base.split("@")[1]
    matching = [charm for charm in charm_files if channel in Path(charm).name]
    if not matching:
        raise ValueError(f"No charm file built for base {base!r}, got {charm_files}")
    yield matching[0]


@pytest_asyncio.fixture(scope="module")
async def app(ops_test: OpsTest, app_name: str, base: str, charm_file: str):
    """SMTP Integrator charm used for integration testing.

    Build the charm and deploy it along with Anycharm.
    """
    assert ops_test.model
    application = await ops_test.model.deploy(
        f"./{charm_file}",
        application_name=app_name,
        base=base,
    )
    yield application


@pytest_asyncio.fixture(scope="module")
async def any_charm(ops_test: OpsTest, base: str):
    """SMTP Integrator charm used for integration testing.

    Build the charm and deploy it along with Anycharm.
    """
    path_lib = "lib/charms/smtp_integrator/v0/smtp.py"
    smtp_lib = Path(path_lib).read_text(encoding="utf8")
    any_charm_script = Path("tests/integration/any_charm.py").read_text(encoding="utf8")
    src_overwrite = {
        "smtp.py": smtp_lib,
        "any_charm.py": any_charm_script,
    }
    assert ops_test.model
    application = await ops_test.model.deploy(
        "any-charm",
        application_name="any",
        channel="beta",
        base=base,
        # Sync the python-packages here with smtp charm lib PYDEPS
        config={
            "src-overwrite": json.dumps(src_overwrite),
            "python-packages": "pydantic>=2\nemail-validator>=2",
        },
    )
    yield application


@pytest_asyncio.fixture(scope="module")
async def juju_version(ops_test: OpsTest):
    """Juju controller version."""
    _, status, _ = await ops_test.juju("status", "--format", "json")
    status = json.loads(status)
    return status["model"]["version"]
