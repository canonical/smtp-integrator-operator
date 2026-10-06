# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

resource "juju_application" "smtp_integrator" {
  name = var.app_name

  charm {
    name     = "smtp-integrator"
    base     = var.base
    channel  = var.channel
    revision = var.revision
  }

  config      = var.config
  constraints = var.constraints
  units       = var.units
  model_uuid  = var.model_uuid
}
