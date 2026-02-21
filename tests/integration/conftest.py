# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Fixtures for the SMTP Integrator charm integration tests."""

import json
import typing
from collections.abc import Generator
from pathlib import Path

import jubilant
import pytest
import yaml


@pytest.fixture(scope="module", name="app_name")
def app_name_fixture():
    """Provide app name from the metadata."""
    metadata = yaml.safe_load(Path("./metadata.yaml").read_text("utf-8"))
    return metadata["name"]


@pytest.fixture(scope="session", name="juju")
def juju_fixture(request: pytest.FixtureRequest) -> Generator[jubilant.Juju, None, None]:
    """Pytest fixture that wraps jubilant.with_model."""

    def show_debug_log(juju: jubilant.Juju):
        """Show debug log.

        Args:
            juju: the Juju object.
        """
        if request.session.testsfailed:
            log = juju.debug_log(limit=1000)
            print(log, end="")

    use_existing = request.config.getoption("--use-existing", default=False)
    if use_existing:
        juju = jubilant.Juju()
        yield juju
        show_debug_log(juju)
        return

    model = request.config.getoption("--model")
    if model:
        juju = jubilant.Juju(model=model)
        yield juju
        show_debug_log(juju)
        return

    keep_models = typing.cast(bool, request.config.getoption("--keep-models"))
    with jubilant.temp_model(keep=keep_models) as juju:
        juju.wait_timeout = 10 * 60
        yield juju
        show_debug_log(juju)
        return


@pytest.fixture(scope="module", name="charm")
def charm_fixture(pytestconfig: pytest.Config):
    """Get value from parameter charm-file."""
    charm = pytestconfig.getoption("--charm-file")
    use_existing = pytestconfig.getoption("--use-existing", default=False)
    if not use_existing:
        assert charm, "--charm-file must be set"
    return charm


@pytest.fixture(scope="module")
def app(juju: jubilant.Juju, charm: str, app_name: str):
    """SMTP Integrator charm used for integration testing."""
    juju.deploy(f"./{charm}", app_name, base="ubuntu@22.04")
    return app_name


# renovate: depName="any-charm"
ANY_CHARM_REVISION = 39


@pytest.fixture(scope="module")
def any_charm(juju: jubilant.Juju):
    """Deploy any-charm for testing.

    Build the charm and deploy it along with the SMTP library.
    """
    path_lib = "lib/charms/smtp_integrator/v0/smtp.py"
    smtp_lib = Path(path_lib).read_text(encoding="utf8")
    any_charm_script = Path("tests/integration/any_charm.py").read_text(encoding="utf8")
    src_overwrite = {
        "smtp.py": smtp_lib,
        "any_charm.py": any_charm_script,
    }
    juju.deploy(
        "any-charm",
        "any",
        channel="latest/edge",
        revision=ANY_CHARM_REVISION,
        base="ubuntu@22.04",
        # Sync the python-packages here with smtp charm lib PYDEPS
        config={
            "src-overwrite": json.dumps(src_overwrite),
            "python-packages": "pydantic>=2\nemail-validator>=2",
        },
    )
    return "any"


@pytest.fixture(scope="module")
def juju_version(juju: jubilant.Juju):
    """Juju controller version."""
    status = juju.status()
    return status.model.version
