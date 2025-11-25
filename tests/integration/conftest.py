# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Fixtures for the SMTP Integrator charm integration tests."""

import json
from pathlib import Path

import pytest_asyncio
import yaml
from pytest import Config, fixture
from pytest_operator.plugin import OpsTest


@fixture(scope="module", name="app_name")
def app_name_fixture():
    """Provide app name from the metadata."""
    metadata = yaml.safe_load(Path("./metadata.yaml").read_text("utf-8"))
    yield metadata["name"]


@pytest_asyncio.fixture(scope="module")
async def app(ops_test: OpsTest, pytestconfig: Config, app_name: str):
    """SMTP Integrator charm used for integration testing.

    Build the charm and deploy it along with Anycharm.
    """
    charm = pytestconfig.getoption("--charm-file")
    assert ops_test.model
    application = await ops_test.model.deploy(
        f"./{charm}",
        application_name=app_name,
        series="jammy",
    )
    yield application


@pytest_asyncio.fixture(scope="module")
async def any_charm(ops_test: OpsTest):
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
        series="jammy"
        # Sync the python-packages here with smtp charm lib PYDEPS
        config={"src-overwrite": json.dumps(src_overwrite), "python-packages": "pydantic>=2"},
    )
    yield application


@pytest_asyncio.fixture(scope="module")
async def juju_version(ops_test: OpsTest):
    """Juju controller version."""
    _, status, _ = await ops_test.juju("status", "--format", "json")
    status = json.loads(status)
    return status["model"]["version"]
