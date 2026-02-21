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
    revision = 118
  }

  assert {
    condition     = output.app_name == "smtp-integrator"
    error_message = "smtp-integrator app_name did not match expected"
  }

  assert {
    condition     = output.provides != null
    error_message = "smtp-integrator provides should not be null"
  }

  assert {
    condition     = output.endpoints != null
    error_message = "smtp-integrator endpoints should not be null"
  }
}
