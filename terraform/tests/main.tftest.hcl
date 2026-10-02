# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

run "setup_tests" {
  module {
    source = "./tests/setup"
  }
}

run "basic_deploy" {
  variables {
    model_uuid = run.setup_tests.model_uuid
    channel    = "latest/edge"
    # renovate: depName="smtp-integrator"
    revision = 131
  }

  assert {
    condition     = output.application.name == "smtp-integrator"
    error_message = "smtp-integrator application name did not match expected"
  }
}
